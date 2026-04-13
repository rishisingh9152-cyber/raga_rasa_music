"""
Cloud Storage Abstraction Layer
Supports multiple storage providers: Local, Cloudinary, Google Drive, AWS S3, Azure Blob
Provides a unified interface for all storage operations
"""

import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import hashlib
from app.config import settings

# Try to import cloudinary, but don't fail if not installed
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

logger = logging.getLogger(__name__)


class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    async def upload_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """Upload a file to storage"""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """Download a file from storage"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        pass
    
    @abstractmethod
    async def list_files(self, folder_path: str = "") -> list:
        """List files in a folder"""
        pass
    
    @abstractmethod
    async def get_download_url(self, file_path: str, expires_in_hours: int = 24) -> str:
        """Get a download URL for a file"""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if a file exists"""
        pass
    
    @abstractmethod
    async def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        pass


class LocalStorageProvider(StorageProvider):
    """Local file system storage provider"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or settings.STORAGE_BASE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorage initialized with base path: {self.base_path}")
    
    async def upload_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """Upload file to local storage"""
        try:
            full_path = self.base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'wb') as f:
                f.write(file_content)
            
            # Calculate file hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            logger.info(f"File uploaded locally: {file_path}")
            return {
                "file_path": file_path,
                "full_path": str(full_path),
                "url": f"/api/songs/stream/{file_path}",
                "size": len(file_content),
                "hash": file_hash
            }
        except Exception as e:
            logger.error(f"Failed to upload file locally: {e}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from local storage"""
        try:
            full_path = self.base_path / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(full_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted locally: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise
    
    async def list_files(self, folder_path: str = "") -> list:
        """List files in a local folder"""
        try:
            full_path = self.base_path / folder_path
            if not full_path.exists():
                return []
            
            files = []
            for item in full_path.glob("*"):
                if item.is_file():
                    files.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.base_path)),
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
            return files
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise
    
    async def get_download_url(self, file_path: str, expires_in_hours: int = 24) -> str:
        """Get download URL for local storage"""
        # For local storage, return the API streaming endpoint
        return f"/api/songs/stream/{file_path}"
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local storage"""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size from local storage"""
        full_path = self.base_path / file_path
        if full_path.exists():
            return full_path.stat().st_size
        return 0


class GoogleDriveStorageProvider(StorageProvider):
    """Google Drive storage provider"""
    
    def __init__(self):
        self.folder_id = settings.GOOGLE_DRIVE_FOLDER_ID
        self.api_key = settings.GOOGLE_DRIVE_API_KEY
        
        if not self.folder_id or not self.api_key:
            raise ValueError("Google Drive configuration missing: GOOGLE_DRIVE_FOLDER_ID and GOOGLE_DRIVE_API_KEY required")
        
        # TODO: Initialize Google Drive client
        logger.info(f"GoogleDrive storage initialized with folder: {self.folder_id}")
    
    async def upload_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """Upload file to Google Drive"""
        # TODO: Implement Google Drive upload
        raise NotImplementedError("Google Drive upload not yet implemented")
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from Google Drive"""
        # TODO: Implement Google Drive download
        raise NotImplementedError("Google Drive download not yet implemented")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Google Drive"""
        # TODO: Implement Google Drive delete
        raise NotImplementedError("Google Drive delete not yet implemented")
    
    async def list_files(self, folder_path: str = "") -> list:
        """List files in Google Drive"""
        # TODO: Implement Google Drive list
        raise NotImplementedError("Google Drive list not yet implemented")
    
    async def get_download_url(self, file_path: str, expires_in_hours: int = 24) -> str:
        """Get Google Drive download URL"""
        # TODO: Implement signed URL generation
        raise NotImplementedError("Google Drive URL generation not yet implemented")
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in Google Drive"""
        # TODO: Implement
        raise NotImplementedError("Google Drive exists check not yet implemented")
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size from Google Drive"""
        # TODO: Implement
        raise NotImplementedError("Google Drive file size not yet implemented")


class AWS_S3_StorageProvider(StorageProvider):
    """AWS S3 storage provider"""
    
    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET
        self.region = settings.AWS_S3_REGION
        
        if not self.bucket or not self.region:
            raise ValueError("AWS S3 configuration missing: AWS_S3_BUCKET and AWS_S3_REGION required")
        
        # TODO: Initialize S3 client
        logger.info(f"AWS S3 storage initialized with bucket: {self.bucket}")
    
    async def upload_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """Upload file to S3"""
        # TODO: Implement S3 upload
        raise NotImplementedError("S3 upload not yet implemented")
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3"""
        # TODO: Implement S3 download
        raise NotImplementedError("S3 download not yet implemented")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        # TODO: Implement S3 delete
        raise NotImplementedError("S3 delete not yet implemented")
    
    async def list_files(self, folder_path: str = "") -> list:
        """List files in S3"""
        # TODO: Implement S3 list
        raise NotImplementedError("S3 list not yet implemented")
    
    async def get_download_url(self, file_path: str, expires_in_hours: int = 24) -> str:
        """Get S3 presigned download URL"""
        # TODO: Implement presigned URL
        raise NotImplementedError("S3 URL generation not yet implemented")
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        # TODO: Implement
        raise NotImplementedError("S3 exists check not yet implemented")
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size from S3"""
        # TODO: Implement
        raise NotImplementedError("S3 file size not yet implemented")


class AzureBlobStorageProvider(StorageProvider):
    """Azure Blob Storage provider"""
    
    def __init__(self):
        self.container = settings.AZURE_BLOB_CONTAINER
        self.account = settings.AZURE_STORAGE_ACCOUNT
        
        if not self.container or not self.account:
            raise ValueError("Azure configuration missing: AZURE_BLOB_CONTAINER and AZURE_STORAGE_ACCOUNT required")
        
        # TODO: Initialize Azure client
        logger.info(f"Azure Blob storage initialized with container: {self.container}")
    
    async def upload_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """Upload file to Azure Blob"""
        # TODO: Implement Azure upload
        raise NotImplementedError("Azure upload not yet implemented")
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from Azure Blob"""
        # TODO: Implement Azure download
        raise NotImplementedError("Azure download not yet implemented")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Azure Blob"""
        # TODO: Implement Azure delete
        raise NotImplementedError("Azure delete not yet implemented")
    
    async def list_files(self, folder_path: str = "") -> list:
        """List files in Azure Blob"""
        # TODO: Implement Azure list
        raise NotImplementedError("Azure list not yet implemented")
    
    async def get_download_url(self, file_path: str, expires_in_hours: int = 24) -> str:
        """Get Azure SAS download URL"""
        # TODO: Implement SAS URL
        raise NotImplementedError("Azure URL generation not yet implemented")
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in Azure Blob"""
        # TODO: Implement
        raise NotImplementedError("Azure exists check not yet implemented")
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size from Azure Blob"""
        # TODO: Implement
        raise NotImplementedError("Azure file size not yet implemented")


class CloudinaryStorageProvider(StorageProvider):
    """Cloudinary cloud storage provider with Rasa-based organization"""
    
    def __init__(self):
        if not CLOUDINARY_AVAILABLE:
            raise ImportError("cloudinary package required for Cloudinary storage. Install with: pip install cloudinary")
        
        self.cloud_name = settings.CLOUDINARY_CLOUD_NAME
        self.api_key = settings.CLOUDINARY_API_KEY
        self.api_secret = settings.CLOUDINARY_API_SECRET
        self.allowed_rasas = settings.ALLOWED_RASAS  # ["Shringar", "Veer", "Shaant", "Shok"]
        
        if not self.cloud_name or not self.api_key or not self.api_secret:
            raise ValueError("Cloudinary configuration missing: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET required")
        
        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        logger.info(f"Cloudinary storage initialized with cloud: {self.cloud_name}")
        logger.info(f"Allowed Rasas: {self.allowed_rasas}")
    
    def _validate_rasa(self, rasa: str) -> bool:
        """Validate if rasa is in allowed list"""
        return rasa in self.allowed_rasas
    
    def _get_rasa_folder(self, rasa: str) -> str:
        """Get the folder path for a rasa"""
        if not self._validate_rasa(rasa):
            raise ValueError(f"Invalid rasa: {rasa}. Allowed rasas: {self.allowed_rasas}")
        return f"raga-rasa/songs/{rasa}"
    
    async def upload_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """Upload file to Cloudinary with Rasa-based folder structure"""
        try:
            # Extract rasa from metadata
            rasa = metadata.get("rasa") if metadata else None
            if not rasa:
                raise ValueError("Rasa is required for song upload. Allowed values: Shringar, Veer, Shaant, Shok")
            
            # Validate rasa
            if not self._validate_rasa(rasa):
                raise ValueError(f"Invalid rasa: {rasa}. Allowed values: {', '.join(self.allowed_rasas)}")
            
            # Determine file type based on extension
            file_name = Path(file_path).name
            rasa_folder = self._get_rasa_folder(rasa)
            
            # Create unique public_id for the file
            public_id = f"{rasa_folder}/{Path(file_path).stem}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                resource_type="auto",  # auto-detect audio/video/image
                public_id=public_id,
                use_filename=True,
                unique_filename=False,
                overwrite=False
            )
            
            logger.info(f"File uploaded to Cloudinary: {file_path} in rasa folder: {rasa}")
            return {
                "file_path": file_path,
                "url": result["secure_url"],
                "cloudinary_url": result["url"],
                "public_id": result["public_id"],
                "size": result.get("bytes", 0),
                "hash": result.get("etag", ""),
                "rasa": rasa
            }
        except Exception as e:
            logger.error(f"Failed to upload file to Cloudinary: {e}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from Cloudinary (not typically used, use URL directly)"""
        try:
            import urllib.request
            # Get the resource
            resources = cloudinary.api.resources(
                resource_type="auto",
                max_results=1,
                prefix=file_path
            )
            
            if not resources.get("resources"):
                raise FileNotFoundError(f"File not found on Cloudinary: {file_path}")
            
            url = resources["resources"][0]["secure_url"]
            with urllib.request.urlopen(url) as response:
                return response.read()
        except Exception as e:
            logger.error(f"Failed to download file from Cloudinary: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Cloudinary"""
        try:
            public_id = file_path.replace("/", "_").replace(".", "_")
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type="auto",
                invalidate=True
            )
            
            if result.get("result") == "ok":
                logger.info(f"File deleted from Cloudinary: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file from Cloudinary: {e}")
            raise
    
    async def list_files(self, folder_path: str = "") -> list:
        """List files in Cloudinary folder (Rasa-based)"""
        try:
            # folder_path should be a rasa name like "Shringar", "Veer", etc.
            if folder_path and not self._validate_rasa(folder_path):
                logger.warning(f"Invalid rasa folder: {folder_path}. Using all rasas.")
                folder_path = ""
            
            if folder_path:
                prefix = f"raga-rasa/songs/{folder_path}"
            else:
                prefix = "raga-rasa/songs"
            
            resources = cloudinary.api.resources(
                resource_type="auto",
                prefix=prefix,
                max_results=100
            )
            
            files = []
            for resource in resources.get("resources", []):
                public_id = resource["public_id"]
                # Extract rasa from path (e.g., "raga-rasa/songs/Shringar/song_name")
                parts = public_id.split("/")
                rasa = parts[2] if len(parts) >= 3 else "Unknown"
                
                files.append({
                    "name": parts[-1] if len(parts) > 0 else resource["public_id"],
                    "path": public_id,
                    "size": resource.get("bytes", 0),
                    "modified": resource.get("created_at", ""),
                    "url": resource.get("secure_url", ""),
                    "rasa": rasa
                })
            return files
        except Exception as e:
            logger.error(f"Failed to list files on Cloudinary: {e}")
            return []
    
    async def get_download_url(self, file_path: str, expires_in_hours: int = 24) -> str:
        """Get Cloudinary download URL (permanent secure URL)"""
        try:
            public_id = file_path.replace("/", "_").replace(".", "_")
            url = cloudinary.utils.cloudinary_url(
                public_id,
                resource_type="auto",
                secure=True
            )[0]
            return url
        except Exception as e:
            logger.error(f"Failed to get download URL from Cloudinary: {e}")
            raise
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists on Cloudinary"""
        try:
            public_id = file_path.replace("/", "_").replace(".", "_")
            resources = cloudinary.api.resources(
                resource_type="auto",
                max_results=1,
                prefix=public_id
            )
            return len(resources.get("resources", [])) > 0
        except Exception as e:
            logger.error(f"Failed to check file existence on Cloudinary: {e}")
            return False
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size from Cloudinary"""
        try:
            public_id = file_path.replace("/", "_").replace(".", "_")
            resources = cloudinary.api.resources(
                resource_type="auto",
                max_results=1,
                prefix=public_id
            )
            
            if resources.get("resources"):
                return resources["resources"][0].get("bytes", 0)
            return 0
        except Exception as e:
            logger.error(f"Failed to get file size from Cloudinary: {e}")
            return 0


class StorageFactory:
    """Factory to create storage providers based on configuration"""
    
    _provider_instance: Optional[StorageProvider] = None
    
    @classmethod
    def get_provider(cls) -> StorageProvider:
        """Get or create storage provider instance"""
        if cls._provider_instance is None:
            provider_type = settings.STORAGE_PROVIDER.lower()
            
            try:
                if provider_type == "local":
                    cls._provider_instance = LocalStorageProvider()
                elif provider_type == "cloudinary":
                    cls._provider_instance = CloudinaryStorageProvider()
                elif provider_type == "google_drive":
                    cls._provider_instance = GoogleDriveStorageProvider()
                elif provider_type == "aws_s3":
                    cls._provider_instance = AWS_S3_StorageProvider()
                elif provider_type == "azure_blob":
                    cls._provider_instance = AzureBlobStorageProvider()
                else:
                    logger.warning(f"Unknown storage provider: {provider_type}, defaulting to local")
                    cls._provider_instance = LocalStorageProvider()
            except Exception as provider_err:
                logger.error(f"Storage provider init failed ({provider_type}): {provider_err}. Falling back to local storage.")
                cls._provider_instance = LocalStorageProvider()
        
        return cls._provider_instance
    
    @classmethod
    def reset(cls):
        """Reset provider instance (useful for testing)"""
        cls._provider_instance = None


# Convenience function to get current provider
def get_storage_provider() -> StorageProvider:
    """Get the current storage provider"""
    return StorageFactory.get_provider()
