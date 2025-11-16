"""
Database initialization script for chat tables
Run this to create chat_rooms and chat_messages tables
"""

from app import app, db
from models import ChatRoom, ChatMessage, User
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_chat_tables():
    """Initialize chat tables in the database"""
    with app.app_context():
        try:
            logger.info("Starting chat tables initialization...")
            
            # Create all tables (including chat tables)
            db.create_all()
            logger.info("✓ All tables created successfully")
            
            # Verify chat_rooms table exists
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'chat_rooms'
            """))
            
            if result.fetchone():
                logger.info("✓ chat_rooms table exists")
            else:
                logger.error("✗ chat_rooms table not found")
                return False
            
            # Verify chat_messages table exists
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'chat_messages'
            """))
            
            if result.fetchone():
                logger.info("✓ chat_messages table exists")
            else:
                logger.error("✗ chat_messages table not found")
                return False
            
            # Check table structure
            logger.info("\nChat Rooms table structure:")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'chat_rooms'
                ORDER BY ordinal_position
            """))
            
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
            
            logger.info("\nChat Messages table structure:")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'chat_messages'
                ORDER BY ordinal_position
            """))
            
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
            
            # Count existing records
            chat_rooms_count = ChatRoom.query.count()
            chat_messages_count = ChatMessage.query.count()
            
            logger.info(f"\n✓ Existing chat rooms: {chat_rooms_count}")
            logger.info(f"✓ Existing chat messages: {chat_messages_count}")
            
            logger.info("\n✅ Chat tables initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"\n✗ Error initializing chat tables: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_chat_functionality():
    """Test basic chat functionality"""
    with app.app_context():
        try:
            logger.info("\n" + "="*50)
            logger.info("Testing chat functionality...")
            logger.info("="*50)
            
            # Get a teacher and student
            teacher = User.query.filter_by(role='teacher').first()
            student = User.query.filter_by(role='student').first()
            
            if not teacher:
                logger.warning("⚠ No teacher found in database. Please register a teacher first.")
                return False
            
            if not student:
                logger.warning("⚠ No student found in database. Please register a student first.")
                return False
            
            logger.info(f"✓ Found teacher: {teacher.name} (ID: {teacher.id})")
            logger.info(f"✓ Found student: {student.name} (ID: {student.id})")
            
            # Check if chat room already exists
            existing_room = ChatRoom.query.filter_by(
                teacher_id=teacher.id,
                student_id=student.id
            ).first()
            
            if existing_room:
                logger.info(f"✓ Chat room already exists (ID: {existing_room.id})")
                chat_room = existing_room
            else:
                # Create a test chat room
                logger.info("Creating test chat room...")
                chat_room = ChatRoom(
                    teacher_id=teacher.id,
                    student_id=student.id
                )
                db.session.add(chat_room)
                db.session.commit()
                logger.info(f"✓ Test chat room created (ID: {chat_room.id})")
            
            # Create a test message
            logger.info("Creating test message...")
            test_message = ChatMessage(
                chat_room_id=chat_room.id,
                sender_id=teacher.id,
                message="This is a test message from the initialization script"
            )
            db.session.add(test_message)
            
            # Update chat room
            chat_room.last_message = test_message.message
            chat_room.last_message_at = test_message.created_at
            chat_room.unread_count_student += 1
            
            db.session.commit()
            logger.info(f"✓ Test message created (ID: {test_message.id})")
            
            # Verify the data
            logger.info("\nVerifying data...")
            room = ChatRoom.query.get(chat_room.id)
            logger.info(f"✓ Chat room: {room.teacher.name} ↔ {room.student.name}")
            logger.info(f"  Last message: {room.last_message}")
            logger.info(f"  Unread (teacher): {room.unread_count_teacher}")
            logger.info(f"  Unread (student): {room.unread_count_student}")
            
            messages = ChatMessage.query.filter_by(chat_room_id=chat_room.id).all()
            logger.info(f"✓ Total messages in room: {len(messages)}")
            
            for msg in messages[-3:]:  # Show last 3 messages
                logger.info(f"  - {msg.sender.name}: {msg.message[:50]}...")
            
            logger.info("\n✅ Chat functionality test completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"\n✗ Error testing chat functionality: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CHAT DATABASE INITIALIZATION")
    print("="*60 + "\n")
    
    # Initialize tables
    if init_chat_tables():
        print("\n" + "="*60)
        print("TESTING CHAT FUNCTIONALITY")
        print("="*60 + "\n")
        
        # Test functionality
        test_chat_functionality()
    
    print("\n" + "="*60)
    print("INITIALIZATION COMPLETE")
    print("="*60 + "\n")
