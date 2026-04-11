# Dropbox Storage Provider Implementation Guide

## **WHAT WE'RE BUILDING**

A working Dropbox integration that allows:
- Upload songs to Dropbox app folder
- Download/stream songs from Dropbox
- Get shareable links
- Fallback to local storage if Dropbox unavailable

---

## **STEP 1: Create Dropbox App**

### Create App
1. Go to https://www.dropbox.com/developers/apps
2. Click "Create app"
3. Fill in:
   - **API**: "Scoped API"
   - **Type of access**: "App folder"
   - **App name**: `raga-rasa-songs`
4. Click "Create app"

### Get Access Token
1. In app settings, scroll to "OAuth 2.0"
2. Click "Generate" in "Access tokens" section
3. Copy the token (format: `sl.Bxxxxxxxxxxxx`)
4. **⚠️ KEEP THIS SECRET** - Don't share or commit to GitHub

### Save Token
Create file `DROPBOX_CREDENTIALS.txt` (don't commit!):
```
DROPBOX_ACCESS_TOKEN=sl.Bxxxxxxxxxxxx
```

---

## **STEP 2: Add Dependencies**

Update `Backend/requirements.txt`:

```
# ... existing packages

# Dropbox SDK
dropbox==11.36.2
```

Install locally:
```bash
pip install dropbox==11.36.2
```

---

## **STEP 3: Implement DropboxStorageProvider**

Update `Backend/app/services/cloud_storage.py` and add this implementation:

```python
class DropboxStorageProvider(StorageProvider):
    """Dropbox storage provider"""
    
    def __init__(self):
        import dropbox
        from dropbox.exceptions import AuthError
        
        self.access_token = settings.DROPBOX_ACCESS_TOKEN
        
        if not self.access_token:
            raise ValueError("Dropbox access token not configured: DROPBOX_ACCESS_TOKEN required")
        
        try:
            self.dbx = dropbox.Dropbox(self.access_token)
            # Test connection
            self.dbx.users_get_current_account()
            logger.info("Dropbox storage initialized successfully")
        except AuthError as e:
            raise ValueError(f"Dropbox authentication failed: {e}")
    
    async def upload_file(self, file_path: str, file_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """Upload file to Dropbox"""
        try:
            # Construct Dropbox path
            dropbox_path = f"/{file_path.lstrip('/')}"
            
            # Upload file
            self.dbx.files_upload(
                file_content,
                dropbox_path,
                mode=dropbox.files.WriteMode('overwrite', None),
                autorename=True
            )
            
            # Calculate file hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Get shareable link
            try:
                link_metadata = self.dbx.sharing_create_shared_link_with_settings(
                    dropbox_path,
                    dropbox.sharing.SharedLinkSettings(
                        requested_visibility=dropbox.sharing.RequestedVisibility.public
                    )
                )
                download_url = link_metadata.url.replace('?dl=0', '?dl=1')  # Force download
            except Exception:
                # Link might already exist
                download_url = f"https://www.dropbox.com/home?folder_id=0&path={file_path}"
            
            logger.info(f"File uploaded to Dropbox: {dropbox_path}")
            
            return {
                "file_path": file_path,
                "cloud_path": dropbox_path,
                "url": download_url,
                "size": len(file_content),
                "hash": file_hash
            }
        except Exception as e:
            logger.error(f"Failed to upload file to Dropbox: {e}")
            raise
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from Dropbox"""
        try:
            dropbox_path = f"/{file_path.lstrip('/')}"
            
            # Download file
            metadata, response = self.dbx.files_download(dropbox_path)
            file_content = response.content
            
            logger.info(f"File downloaded from Dropbox: {dropbox_path}")
            return file_content
        except Exception as e:
            logger.error(f"Failed to download file from Dropbox: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from Dropbox"""
        try:
            dropbox_path = f"/{file_path.lstrip('/')}"
            self.dbx.files_delete_v2(dropbox_path)
            logger.info(f"File deleted from Dropbox: {dropbox_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from Dropbox: {e}")
            raise
    
    async def list_files(self, folder_path: str = "") -> list:
        """List files in Dropbox folder"""
        try:
            dropbox_path = f"/{folder_path.lstrip('/')}" if folder_path else ""
            
            result = self.dbx.files_list_folder(dropbox_path)
            
            files = []
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append({
                        "name": entry.name,
                        "path": entry.path_display,
                        "size": entry.size,
                        "modified": entry.server_modified.isoformat()
                    })
            
            return files
        except Exception as e:
            logger.error(f"Failed to list Dropbox files: {e}")
            raise
    
    async def get_download_url(self, file_path: str, expires_in_hours: int = 24) -> str:
        """Get Dropbox download URL"""
        try:
            dropbox_path = f"/{file_path.lstrip('/')}"
            
            try:
                link_metadata = self.dbx.sharing_create_shared_link_with_settings(
                    dropbox_path,
                    dropbox.sharing.SharedLinkSettings(
                        requested_visibility=dropbox.sharing.RequestedVisibility.public
                    )
                )
                # Force download by changing dl=0 to dl=1
                return link_metadata.url.replace('?dl=0', '?dl=1')
            except Exception:
                # If link already exists
                links = self.dbx.sharing_list_shared_links(path=dropbox_path)
                if links.links:
                    return links.links[0].url.replace('?dl=0', '?dl=1')
                raise
        except Exception as e:
            logger.error(f"Failed to get Dropbox URL: {e}")
            raise
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in Dropbox"""
        try:
            dropbox_path = f"/{file_path.lstrip('/')}"
            self.dbx.files_get_metadata(dropbox_path)
            return True
        except Exception:
            return False
    
    async def get_file_size(self, file_path: str) -> int:
        """Get file size from Dropbox"""
        try:
            dropbox_path = f"/{file_path.lstrip('/')}"
            metadata = self.dbx.files_get_metadata(dropbox_path)
            if isinstance(metadata, dropbox.files.FileMetadata):
                return metadata.size
            return 0
        except Exception:
            return 0
```

---

## **STEP 4: Update Configuration**

Add to `Backend/app/config.py`:

```python
# Dropbox Configuration
DROPBOX_ACCESS_TOKEN: Optional[str] = None
```

Update `Backend/.env`:

```ini
# Storage
STORAGE_PROVIDER=dropbox
DROPBOX_ACCESS_TOKEN=sl.Bxxxxxxxxxxxx
```

---

## **STEP 5: Create Folder Structure in Dropbox**

In your Dropbox app folder (it's in `/Apps/raga-rasa-songs/`), create:

```
/Apps/raga-rasa-songs/
├── shaant/
├── shringar/
├── veer/
└── shok/
```

Or they'll be created automatically on first upload.

---

## **STEP 6: Test Locally**

### Test 1: Simple Connection Test

Create file `Backend/test_dropbox.py`:

```python
import asyncio
from app.services.cloud_storage import DropboxStorageProvider

async def test_dropbox():
    try:
        provider = DropboxStorageProvider()
        print("✅ Dropbox connection successful!")
        
        # List files
        files = await provider.list_files("")
        print(f"✅ Files in Dropbox: {len(files)}")
        
    except Exception as e:
        print(f"❌ Dropbox error: {e}")

asyncio.run(test_dropbox())
```

Run:
```bash
cd Backend
python test_dropbox.py
```

Expected output:
```
✅ Dropbox connection successful!
✅ Files in Dropbox: 0
```

### Test 2: Upload & Download Test

```python
import asyncio
from app.services.cloud_storage import DropboxStorageProvider

async def test_upload_download():
    provider = DropboxStorageProvider()
    
    # Create test file content
    test_content = b"This is a test song file"
    
    try:
        # Upload
        result = await provider.upload_file(
            "test/test_song.mp3",
            test_content,
            metadata={"rasa": "Shaant"}
        )
        print(f"✅ Uploaded: {result['file_path']}")
        print(f"   URL: {result['url']}")
        
        # Download
        downloaded = await provider.download_file("test/test_song.mp3")
        if downloaded == test_content:
            print("✅ Download successful - content matches!")
        else:
            print("❌ Download failed - content mismatch")
        
        # Get URL
        url = await provider.get_download_url("test/test_song.mp3")
        print(f"✅ Download URL: {url}")
        
        # Check file exists
        exists = await provider.file_exists("test/test_song.mp3")
        print(f"✅ File exists: {exists}")
        
        # Get file size
        size = await provider.get_file_size("test/test_song.mp3")
        print(f"✅ File size: {size} bytes")
        
        # List files
        files = await provider.list_files("test")
        print(f"✅ Files in test folder: {len(files)}")
        
        # Delete
        deleted = await provider.delete_file("test/test_song.mp3")
        print(f"✅ Deleted: {deleted}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test_upload_download())
```

Expected output:
```
✅ Uploaded: test/test_song.mp3
   URL: https://www.dropbox.com/s/xxxxx/test_song.mp3?dl=1
✅ Download successful - content matches!
✅ Download URL: https://www.dropbox.com/s/xxxxx/test_song.mp3?dl=1
✅ File exists: True
✅ File size: 24 bytes
✅ Files in test folder: 1
✅ Deleted: True
```

### Test 3: Switch to Dropbox and Test Upload

In `Backend/.env`, set:
```ini
STORAGE_PROVIDER=dropbox
DROPBOX_ACCESS_TOKEN=sl.Bxxxxxxxxxxxx
```

Restart backend:
```bash
cd Backend
python -m uvicorn main:app --reload
```

Test upload via API:
```bash
curl -X POST http://localhost:8000/api/songs/upload \
  -F "title=Test Song" \
  -F "artist=Test Artist" \
  -F "emotion=Happy" \
  -F "file=@/path/to/test.mp3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Check Dropbox - file should be there!

---

## **STEP 7: Environment Variables**

### Local Development
Update `Backend/.env`:
```ini
STORAGE_PROVIDER=dropbox
DROPBOX_ACCESS_TOKEN=sl.Bxxxxxxxxxxxx
```

### Render Production
In Render backend service → Environment:
```
STORAGE_PROVIDER=dropbox
DROPBOX_ACCESS_TOKEN=sl.Bxxxxxxxxxxxx
```

---

## **FALLBACK HANDLING**

The system automatically falls back to local storage if Dropbox is unavailable.

In `Backend/app/services/song_upload.py`:

```python
async def move_song_to_rasa_folder(
    temp_path: str, 
    rasa: str, 
    song_title: str,
    use_cloud: bool = False
) -> Dict[str, str]:
    try:
        if use_cloud and settings.STORAGE_PROVIDER == "dropbox":
            try:
                # Try Dropbox
                storage_provider = get_storage_provider()
                # ... upload to Dropbox
            except Exception as e:
                logger.warning(f"Dropbox unavailable, falling back to local: {e}")
                # Fall back to local storage
                use_cloud = False
        
        if not use_cloud:
            # Use local storage
            # ... move to local folder
```

---

## **VERIFICATION CHECKLIST**

- [ ] Dropbox app created at https://www.dropbox.com/developers/apps
- [ ] Access token generated and saved securely
- [ ] Folder structure created in Dropbox app folder
- [ ] `dropbox==11.36.2` added to `requirements.txt`
- [ ] `DropboxStorageProvider` class implemented in `cloud_storage.py`
- [ ] Configuration updated with `DROPBOX_ACCESS_TOKEN`
- [ ] Local connection test passes
- [ ] Upload/download test passes
- [ ] API test works (file in Dropbox)
- [ ] Fallback to local works
- [ ] Environment variables in Render configured

---

## **TROUBLESHOOTING**

### "Invalid access token"
- Copy-paste exact token from Dropbox app settings
- No extra spaces or characters
- Token format should be `sl.Bxxxxx...`

### "File not found" on download
- Check file path format (must start with `/`)
- Verify file was uploaded successfully
- Check Dropbox app folder in web UI

### "Shareable link not found"
- Public visibility must be enabled
- Link is created automatically on first request
- May take a few seconds

### Dropbox API rate limit
- Free tier has 45,000 API calls per day
- That's plenty for our use case
- If exceeded, falls back to local

---

**Status**: Dropbox provider ready! Proceed to Day 3 (Deployment) once all components tested.
