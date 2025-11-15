import os
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

logger = logging.getLogger(__name__)

class S3StorageService:
    def __init__(self, auto_create_bucket: bool = True):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'classroom-assistant-audio')
        self.bucket_created = False
        
        if self.aws_access_key and self.aws_secret_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                )
                logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
                
                # Auto-create bucket if it doesn't exist
                if auto_create_bucket:
                    self._ensure_bucket_exists()
                    
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {str(e)}")
                self.s3_client = None
        else:
            logger.warning("AWS credentials not found in environment variables")
            self.s3_client = None
    
    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists and is accessible")
            self.bucket_created = True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Bucket {self.bucket_name} does not exist, creating...")
                if self.create_bucket():
                    logger.info(f"Bucket {self.bucket_name} created successfully")
                    self.bucket_created = True
                else:
                    logger.error(f"Failed to create bucket {self.bucket_name}")
            elif error_code == '403':
                logger.error(f"Access denied to bucket {self.bucket_name}")
            else:
                logger.error(f"Error checking bucket: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error ensuring bucket exists: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the S3 service is available"""
        if not self.s3_client:
            return False
        
        try:
            # Try to check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"Bucket {self.bucket_name} does not exist, attempting to create...")
                # Try to create bucket
                if self.create_bucket():
                    return True
                logger.error(f"Failed to create bucket {self.bucket_name}")
            elif error_code == '403':
                logger.error(f"Access denied to bucket {self.bucket_name}")
            else:
                logger.error(f"Error checking bucket: {str(e)}")
            return False
        except NoCredentialsError:
            logger.error("AWS credentials not available")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking S3 availability: {str(e)}")
            return False
    
    def upload_audio(self, file_name: str, file_content: bytes) -> Optional[str]:
        """
        Upload audio file to S3
        
        Args:
            file_name: Name of the file to upload
            file_content: Binary content of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        try:
            if not self.s3_client:
                logger.error("S3 client not available - check AWS credentials")
                return None
            
            # Define the S3 key (path in bucket)
            s3_key = f"audio/{file_name}"
            
            logger.info(f"Uploading {file_name} to S3 bucket {self.bucket_name}")
            logger.info(f"File size: {len(file_content)} bytes")
            
            # Determine content type based on file extension
            content_type = self._get_content_type(file_name)
            
            # Upload file to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'  # Make file publicly accessible
            )
            
            # Generate public URL
            public_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Audio file uploaded successfully: {file_name} -> {public_url}")
            return public_url
            
        except ClientError as e:
            logger.error(f"AWS ClientError uploading audio file: {str(e)}")
            logger.error(f"Error code: {e.response['Error']['Code']}")
            return None
        except Exception as e:
            logger.error(f"Error uploading audio file: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def upload_image(self, file_name: str, file_content: bytes, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Upload image file to S3
        
        Args:
            file_name: Name of the file to upload
            file_content: Binary content of the file
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        try:
            if not self.s3_client:
                logger.error("S3 client not available")
                return None
            
            # Define the S3 key (path in bucket)
            s3_key = f"images/profiles/{file_name}"
            
            logger.info(f"Uploading image {file_name} to S3")
            
            # Upload file to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )
            
            # Generate public URL
            public_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Image file uploaded successfully: {file_name}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading image file: {str(e)}")
            return None
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from S3
        
        Args:
            file_key: S3 key (path) of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.s3_client:
                logger.error("S3 client not available")
                return False
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            logger.info(f"File deleted successfully: {file_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_url(self, file_key: str) -> Optional[str]:
        """
        Get public URL for a file in S3
        
        Args:
            file_key: S3 key (path) of the file
            
        Returns:
            Public URL of the file
        """
        try:
            if not self.s3_client:
                logger.error("S3 client not available")
                return None
            
            public_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{file_key}"
            return public_url
            
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            return None
    
    def list_files(self, prefix: str = "") -> Optional[list]:
        """
        List files in S3 bucket with given prefix
        
        Args:
            prefix: Prefix (folder path) to filter files
            
        Returns:
            List of file keys or None if failed
        """
        try:
            if not self.s3_client:
                logger.error("S3 client not available")
                return None
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                logger.info(f"Listed {len(files)} files with prefix {prefix}")
                return files
            else:
                logger.info(f"No files found with prefix {prefix}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return None
    
    def create_bucket(self) -> bool:
        """
        Create S3 bucket if it doesn't exist
        
        Returns:
            True if successful or bucket already exists, False otherwise
        """
        try:
            if not self.s3_client:
                logger.error("S3 client not available")
                return False
            
            # Check if bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} already exists")
                self.bucket_created = True
                return True
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code != '404':
                    logger.error(f"Error checking bucket existence: {str(e)}")
                    raise
            
            logger.info(f"Creating S3 bucket: {self.bucket_name} in region: {self.aws_region}")
            
            # Create bucket
            try:
                if self.aws_region == 'us-east-1':
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                    )
                logger.info(f"Bucket {self.bucket_name} created")
            except ClientError as e:
                if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                    logger.info(f"Bucket {self.bucket_name} already owned by you")
                elif e.response['Error']['Code'] == 'BucketAlreadyExists':
                    logger.error(f"Bucket name {self.bucket_name} is already taken by another AWS account")
                    return False
                else:
                    raise
            
            # Disable Block Public Access settings
            try:
                self.s3_client.delete_public_access_block(Bucket=self.bucket_name)
                logger.info("Public access block removed")
            except Exception as e:
                logger.warning(f"Could not remove public access block: {str(e)}")
            
            # Set bucket policy for public read access
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                    }
                ]
            }
            
            import json
            try:
                self.s3_client.put_bucket_policy(
                    Bucket=self.bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
                logger.info("Bucket policy set for public read access")
            except Exception as e:
                logger.warning(f"Could not set bucket policy: {str(e)}")
                logger.info("Files will still be accessible with ACL='public-read'")
            
            # Enable CORS for web access
            cors_configuration = {
                'CORSRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': ['GET', 'HEAD'],
                        'AllowedOrigins': ['*'],
                        'ExposeHeaders': ['ETag'],
                        'MaxAgeSeconds': 3000
                    }
                ]
            }
            
            try:
                self.s3_client.put_bucket_cors(
                    Bucket=self.bucket_name,
                    CORSConfiguration=cors_configuration
                )
                logger.info("CORS configuration set")
            except Exception as e:
                logger.warning(f"Could not set CORS configuration: {str(e)}")
            
            logger.info(f"✓ Bucket {self.bucket_name} is ready for use")
            self.bucket_created = True
            return True
            
        except Exception as e:
            logger.error(f"Error creating bucket: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _get_content_type(self, file_name: str) -> str:
        """
        Determine content type based on file extension
        
        Args:
            file_name: Name of the file
            
        Returns:
            MIME type string
        """
        extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
        
        content_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'flac': 'audio/flac',
            'ogg': 'audio/ogg',
            'aac': 'audio/aac',
            'webm': 'audio/webm'
        }
        
        return content_types.get(extension, 'application/octet-stream')
