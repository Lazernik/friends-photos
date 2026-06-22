from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app import s3, zip_utils
from app.schemas import UploadResponse

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}


@router.post("/upload", response_model=UploadResponse)
async def upload_photo(file: UploadFile = File(...)) -> UploadResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    suffix = PurePosixPath(file.filename or "photo").suffix or ".jpg"
    key = f"photos/{uuid4().hex}{suffix}"

    try:
        s3.upload_file(file.file, key, content_type=file.content_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc

    return UploadResponse(
        filename=file.filename or key,
        key=key,
        message="Photo uploaded successfully.",
    )


@router.get("/download")
async def download_all_photos() -> Response:
    try:
        files = s3.download_all_files()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list or download files: {exc}") from exc

    if not files:
        raise HTTPException(status_code=404, detail="No photos found in the bucket.")

    archive = zip_utils.create_zip(files)

    return Response(
        content=archive,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="friends-photos.zip"'},
    )
