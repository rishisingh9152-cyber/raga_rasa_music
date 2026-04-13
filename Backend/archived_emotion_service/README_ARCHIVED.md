## Archived Emotion Service

This folder is intentionally archived and is not part of the active production path.

Current architecture uses the integrated backend emotion route:

- `Backend/app/routes/emotion.py`
- `POST /api/detect-emotion`

Frontend session camera capture must call the backend API only. It must not call any separate service from this folder.

If this folder exists in the repository, treat it as historical reference only.
