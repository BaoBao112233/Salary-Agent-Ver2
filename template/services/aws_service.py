import boto3
import os
import logging
from template.configs.environments import env
from botocore.exceptions import (
    ClientError, 
    NoCredentialsError,
    EndpointConnectionError
)

logger = logging.getLogger(__name__)


class S3Service:
    """Service for handling S3 operations for Salary Agent"""
    
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=env.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
            region_name=env.REGION
        )
        self.bucket = env.BUCKET
        self.region = env.REGION
        self.project_name = env.PROJECT_NAME
        
    def upload_file(self, file_path: str, s3_folder: str, filename: str = None) -> str:
        """Upload file to S3 and return S3 key"""
        try:
            if filename is None:
                filename = os.path.basename(file_path)
            
            s3_key = f"{self.project_name}/{s3_folder}/{filename}"
            
            logger.info(f"Uploading {file_path} to s3://{self.bucket}/{s3_key}")
            
            self.s3.upload_file(file_path, self.bucket, s3_key)
            
            logger.info(f"Successfully uploaded to S3: {s3_key}")
            return s3_key
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except NoCredentialsError:
            logger.error("AWS credentials invalid")
            raise
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """Download file from S3 to local path"""
        try:
            logger.info(f"Downloading s3://{self.bucket}/{s3_key} to {local_path}")
            
            self.s3.download_file(self.bucket, s3_key, local_path)
            
            logger.info(f"Successfully downloaded from S3")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            return False
    
    def check_folder_exists(self, folder_path: str) -> bool:
        """Check if a folder exists in S3"""
        try:
            if not folder_path.endswith('/'):
                folder_path += '/'
            
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=folder_path,
                MaxKeys=1
            )
            
            return 'Contents' in response
            
        except Exception as e:
            logger.error(f"Error checking folder: {str(e)}")
            return False
    
    def create_folder(self, folder_path: str) -> bool:
        """Create a folder in S3"""
        try:
            if not folder_path.endswith('/'):
                folder_path += '/'
            
            self.s3.put_object(
                Bucket=self.bucket,
                Key=folder_path,
                Body=b'',
                ContentType='application/x-directory'
            )
            
            logger.info(f"Created folder: {folder_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return False
    
    def ensure_folders_exist(self):
        """Ensure required folders exist in S3"""
        folders = [
            f"{self.project_name}/",
            f"{self.project_name}/salary/",
            f"{self.project_name}/attendance/",
            f"{self.project_name}/outputs/",
        ]
        
        for folder in folders:
            if not self.check_folder_exists(folder):
                logger.info(f"Creating folder: {folder}")
                self.create_folder(folder)
            else:
                logger.info(f"Folder already exists: {folder}")
    
    def get_file_url(self, s3_key: str) -> str:
        """Get public URL for S3 file"""
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"

