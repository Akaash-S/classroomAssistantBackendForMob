from flask import Blueprint, request, jsonify
from models import Task, TaskStatus, TaskPriority, User, Lecture, db
from datetime import datetime
import logging

tasks_bp = Blueprint('tasks', __name__)
logger = logging.getLogger(__name__)

@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    try:
        user_id = request.args.get('user_id')
        teacher_id = request.args.get('teacher_id')  # NEW: For teachers to get tasks from their lectures
        lecture_id = request.args.get('lecture_id')  # NEW: Filter by specific lecture
        status = request.args.get('status')
        priority = request.args.get('priority')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = Task.query
        
        # Filter by assigned student
        if user_id:
            query = query.filter_by(assigned_to_id=user_id)
        
        # Filter by teacher's lectures (for teacher view)
        if teacher_id:
            # Get all lectures by this teacher
            teacher_lectures = Lecture.query.filter_by(teacher_id=teacher_id).all()
            lecture_ids = [lecture.id for lecture in teacher_lectures]
            
            if lecture_ids:
                query = query.filter(Task.lecture_id.in_(lecture_ids))
            else:
                # Teacher has no lectures, return empty
                return jsonify({
                    'status': 'success',
                    'tasks': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset
                }), 200
        
        # Filter by specific lecture
        if lecture_id:
            query = query.filter_by(lecture_id=lecture_id)
        
        # Filter by status
        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid status value'
                }), 400
        
        # Filter by priority
        if priority:
            try:
                priority_enum = TaskPriority(priority)
                query = query.filter_by(priority=priority_enum)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid priority value'
                }), 400
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering
        tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'tasks': [task.to_dict() for task in tasks],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Get tasks error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get tasks'
        }), 500

@tasks_bp.route('/', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate priority if provided
        priority = TaskPriority.MEDIUM
        if 'priority' in data:
            try:
                priority = TaskPriority(data['priority'])
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid priority value'
                }), 400
        
        # Validate status if provided
        status = TaskStatus.PENDING
        if 'status' in data:
            try:
                status = TaskStatus(data['status'])
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid status value'
                }), 400
        
        # Validate due_date if provided
        due_date = None
        if 'due_date' in data and data['due_date']:
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid due_date format'
                }), 400
        
        # Create new task
        task = Task(
            title=data['title'],
            description=data['description'],
            lecture_id=data.get('lecture_id'),
            assigned_to_id=data.get('assigned_to_id'),
            status=status,
            priority=priority,
            due_date=due_date,
            is_ai_generated=data.get('is_ai_generated', False)
        )
        
        db.session.add(task)
        db.session.commit()
        
        logger.info(f"New task created: {task.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create task error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create task'
        }), 500

@tasks_bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get task error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get task'
        }), 500

@tasks_bp.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'assigned_to_id', 'priority', 'due_date']
        
        for field in allowed_fields:
            if field in data:
                if field == 'priority':
                    try:
                        setattr(task, field, TaskPriority(data[field]))
                    except ValueError:
                        return jsonify({
                            'status': 'error',
                            'message': 'Invalid priority value'
                        }), 400
                elif field == 'due_date' and data[field]:
                    try:
                        setattr(task, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                    except ValueError:
                        return jsonify({
                            'status': 'error',
                            'message': 'Invalid due_date format'
                        }), 400
                else:
                    setattr(task, field, data[field])
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Task updated: {task.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update task error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update task'
        }), 500

@tasks_bp.route('/<task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Status is required'
            }), 400
        
        try:
            new_status = TaskStatus(data['status'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid status value'
            }), 400
        
        task.status = new_status
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Task status updated: {task.title} -> {new_status.value}")
        
        return jsonify({
            'status': 'success',
            'message': 'Task status updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update task status error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update task status'
        }), 500

@tasks_bp.route('/<task_id>/approve', methods=['POST'])
def approve_task(task_id):
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        task.status = TaskStatus.APPROVED
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Task approved: {task.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Task approved successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Approve task error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to approve task'
        }), 500

@tasks_bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        db.session.delete(task)
        db.session.commit()
        
        logger.info(f"Task deleted: {task.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Task deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete task error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete task'
        }), 500
