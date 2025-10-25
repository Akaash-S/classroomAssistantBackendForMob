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
        
        if self.supabase_url and self.supabase_key:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            self.client = None
    
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
                logger.error("Supabase client not available")
                return None
            
            # Upload to the 'lectures' bucket
            bucket_name = 'lectures'
            file_path = f"audio/{file_name}"
            
            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "audio/mpeg"}
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
                logger.info(f"Audio file uploaded successfully: {file_name}")
                return public_url
            else:
                logger.error(f"Failed to upload audio file: {file_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading audio file: {str(e)}")
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
    
    def delete_file(self, bucket_name: str, file_path: str) -> bool:
        """
        Delete file from Supabase storage
        
        Args:
            bucket_name: Name of the bucket
            file_path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                logger.error("Supabase client not available")
                return False
            
            response = self.client.storage.from_(bucket_name).remove([file_path])
            
            if response:
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.error(f"Failed to delete file: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_url(self, bucket_name: str, file_path: str) -> Optional[str]:
        """
        Get public URL for a file in Supabase storage
        
        Args:
            bucket_name: Name of the bucket
            file_path: Path to the file
            
        Returns:
            Public URL of the file or None if failed
        """
        try:
            if not self.client:
                logger.error("Supabase client not available")
                return None
            
            public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
            return public_url
            
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            return None
    
    def list_files(self, bucket_name: str, folder_path: str = "") -> Optional[list]:
        """
        List files in a Supabase storage bucket
        
        Args:
            bucket_name: Name of the bucket
            folder_path: Path to the folder to list
            
        Returns:
            List of files or None if failed
        """
        try:
            if not self.client:
                logger.error("Supabase client not available")
                return None
            
            response = self.client.storage.from_(bucket_name).list(folder_path)
            
            if response:
                logger.info(f"Listed {len(response)} files in {bucket_name}/{folder_path}")
                return response
            else:
                logger.error(f"Failed to list files in {bucket_name}/{folder_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return None
    
    def create_bucket(self, bucket_name: str, is_public: bool = True) -> bool:
        """
        Create a new bucket in Supabase storage
        
        Args:
            bucket_name: Name of the bucket to create
            is_public: Whether the bucket should be public
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                logger.error("Supabase client not available")
                return False
            
            # Use service key for admin operations
            if self.supabase_service_key:
                admin_client = create_client(self.supabase_url, self.supabase_service_key)
                response = admin_client.storage.create_bucket(
                    bucket_name,
                    options={"public": is_public}
                )
            else:
                response = self.client.storage.create_bucket(
                    bucket_name,
                    options={"public": is_public}
                )
            
            if response:
                logger.info(f"Bucket created successfully: {bucket_name}")
                return True
            else:
                logger.error(f"Failed to create bucket: {bucket_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating bucket: {str(e)}")
            return False
    
    def list_buckets(self) -> Optional[list]:
        """
        List all buckets in Supabase storage
        
        Returns:
            List of buckets or None if failed
        """
        try:
            if not self.client:
                logger.error("Supabase client not available")
                return None
            
            # Use service key for admin operations
            if self.supabase_service_key:
                admin_client = create_client(self.supabase_url, self.supabase_service_key)
                response = admin_client.storage.list_buckets()
            else:
                response = self.client.storage.list_buckets()
            
            if response:
                # Handle different response formats
                if isinstance(response, list):
                    buckets = []
                    for bucket in response:
                        if hasattr(bucket, 'name'):
                            buckets.append(bucket.name)
                        elif isinstance(bucket, dict):
                            buckets.append(bucket.get('name', str(bucket)))
                        else:
                            buckets.append(str(bucket))
                else:
                    # If response is a single object
                    if hasattr(response, 'name'):
                        buckets = [response.name]
                    else:
                        buckets = [str(response)]
                logger.info(f"Found {len(buckets)} buckets")
                return buckets
            else:
                logger.error("Failed to list buckets")
                return None
                
        except Exception as e:
            logger.error(f"Error listing buckets: {str(e)}")
            return None
