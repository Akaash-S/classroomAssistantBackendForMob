import os
import logging
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        # Only initialize if we have valid-looking credentials
        if (self.supabase_url and self.supabase_url.startswith('https://') and 
            self.supabase_key and not self.supabase_key.startswith('your-')):
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                self.client = None
        else:
            self.client = None
            if self.supabase_url or self.supabase_key:
                logger.warning("Supabase credentials appear to be placeholders or invalid. Client NOT initialized.")
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return bool(self.client)
    
    def upload_audio(self, file_name: str, file_content: bytes) -> Optional[str]:
        """
        Upload audio file to Supabase storage
        
        Args:
            file_name: Name of the file to upload
            file_content: Binary content of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        try:
            if not self.client:
                logger.error("Supabase client not available - check SUPABASE_URL and SUPABASE_KEY environment variables")
                return None
            
            # Check if credentials are set
            if not self.supabase_url or not self.supabase_key:
                logger.error(f"Supabase credentials missing - URL: {bool(self.supabase_url)}, KEY: {bool(self.supabase_key)}")
                return None
            
            # Upload to the 'lectures' bucket
            bucket_name = 'lectures'
            file_path = f"audio/{file_name}"
            
            logger.info(f"Attempting to upload {file_name} to bucket {bucket_name}")
            logger.info(f"File size: {len(file_content)} bytes")
            
            # Check if bucket exists first
            try:
                buckets = self.list_buckets()
                if buckets and bucket_name not in buckets:
                    logger.warning(f"Bucket {bucket_name} does not exist. Available buckets: {buckets}")
                    # Try to create the bucket
                    if self.create_bucket(bucket_name, is_public=True):
                        logger.info(f"Created bucket {bucket_name}")
                    else:
                        logger.error(f"Failed to create bucket {bucket_name}")
                        return None
            except Exception as bucket_error:
                logger.warning(f"Could not check buckets: {bucket_error}")
            
            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "audio/mpeg"}
            )
            
            logger.info(f"Upload response: {response}")
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
                logger.info(f"Audio file uploaded successfully: {file_name} -> {public_url}")
                return public_url
            else:
                logger.error(f"Upload response was empty for file: {file_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading audio file: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def upload_image(self, file_name: str, file_content: bytes, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Upload image file to Supabase storage
        
        Args:
            file_name: Name of the file to upload
            file_content: Binary content of the file
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        try:
            if not self.client:
                logger.error("Supabase client not available")
                return None
            
            # Upload to the 'images' bucket
            bucket_name = 'images'
            file_path = f"profiles/{file_name}"
            
            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": content_type}
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
                logger.info(f"Image file uploaded successfully: {file_name}")
                return public_url
            else:
                logger.error(f"Failed to upload image file: {file_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading image file: {str(e)}")
            return None
    
    def upload_document(self, file_name: str, file_content: bytes, room_id: str, content_type: str = None) -> Optional[str]:
        """
        Upload document file to Supabase storage
        
        Args:
            file_name: Name of the file to upload
            file_content: Binary content of the file
            room_id: Chat room ID for organizing documents
            content_type: MIME type of the file (optional)
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        try:
            if not self.client:
                logger.error("Supabase client not available")
                return None
            
            # Upload to the 'documents' bucket
            bucket_name = 'documents'
            
            # Generate unique filename to avoid conflicts (similar to S3 implementation)
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{file_name}"
            file_path = f"{room_id}/{unique_filename}"
            
            # Determine content type if not provided
            if not content_type:
                extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
                content_types = {
                    'pdf': 'application/pdf',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'txt': 'text/plain'
                }
                content_type = content_types.get(extension, 'application/octet-stream')

            # Check if bucket exists
            try:
                buckets = self.list_buckets()
                if buckets and bucket_name not in buckets:
                    self.create_bucket(bucket_name, is_public=True)
            except:
                pass

            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": content_type}
            )
            
            if response:
                public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
                logger.info(f"Document uploaded successfully: {file_name} -> {public_url}")
                return public_url
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return None

    def delete_file(self, file_path: str, bucket_name: str = 'lectures') -> bool:
        """
        Delete file from Supabase storage
        
        Args:
            file_path: Path to the file to delete (e.g., 'audio/filename.mp3' or 'profiles/image.jpg')
            bucket_name: Name of the bucket (defaults to 'lectures')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                return False
            
            # If path starts with 'profiles/', it's probably in the images bucket
            if file_path.startswith('profiles/') and bucket_name == 'lectures':
                bucket_name = 'images'
            # If path starts with documents, it's in documents bucket
            elif '/' in file_path and bucket_name == 'lectures':
                # Check if it looks like a document path (uuid/filename)
                potential_room_id = file_path.split('/')[0]
                if len(potential_room_id) > 10: # Likely a UUID or long ID
                    bucket_name = 'documents'

            response = self.client.storage.from_(bucket_name).remove([file_path])
            return bool(response)
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str, bucket_name: str = 'lectures') -> Optional[str]:
        """
        Get public URL for a file in Supabase storage
        """
        try:
            if not self.client:
                return None
            
            if file_path.startswith('profiles/') and bucket_name == 'lectures':
                bucket_name = 'images'
            
            return self.client.storage.from_(bucket_name).get_public_url(file_path)
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            return None
    
    def list_files(self, folder_path: str = "", bucket_name: str = 'lectures') -> Optional[list]:
        """
        List files in a Supabase storage bucket
        """
        try:
            if not self.client:
                return None
            return self.client.storage.from_(bucket_name).list(folder_path)
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return None

    def create_bucket(self, bucket_name: str, is_public: bool = True) -> bool:
        """
        Create a new bucket in Supabase storage
        """
        try:
            if not self.client:
                return False
            
            # Use service key for admin operations if available
            client_to_use = self.client
            if self.supabase_service_key:
                client_to_use = create_client(self.supabase_url, self.supabase_service_key)
            
            response = client_to_use.storage.create_bucket(
                bucket_name,
                options={"public": is_public}
            )
            return bool(response)
        except Exception as e:
            logger.error(f"Error creating bucket: {str(e)}")
            return False
    
    def list_buckets(self) -> Optional[list]:
        """
        List all buckets in Supabase storage
        """
        try:
            if not self.client:
                return None
            
            client_to_use = self.client
            if self.supabase_service_key:
                client_to_use = create_client(self.supabase_url, self.supabase_service_key)
            
            response = client_to_use.storage.list_buckets()
            
            if response:
                buckets = []
                for bucket in response:
                    if hasattr(bucket, 'name'):
                        buckets.append(bucket.name)
                    elif isinstance(bucket, dict):
                        buckets.append(bucket.get('name', str(bucket)))
                return buckets
            return []
        except Exception as e:
            logger.error(f"Error listing buckets: {str(e)}")
            return None
