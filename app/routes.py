from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.security import HTTPBasicCredentials

from app import s3, zip_utils
from app.auth import verify_password
from app.schemas import UploadResponse, UploadedFile

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
    "video/mpeg",
    "video/3gpp",
}

DEFAULT_SUFFIX_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
    "video/x-msvideo": ".avi",
    "video/x-matroska": ".mkv",
    "video/mpeg": ".mpeg",
    "video/3gpp": ".3gp",
}


@router.get("/auth/check")
async def auth_check(_: HTTPBasicCredentials = Depends(verify_password)) -> dict[str, bool]:
    return {"ok": True}


@router.post("/upload", response_model=UploadResponse)
async def upload_photos(
    files: list[UploadFile] = File(...),
    _: HTTPBasicCredentials = Depends(verify_password),
) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    uploaded: list[UploadedFile] = []

    for file in files:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Only image and video files are allowed. Invalid file: {file.filename or 'unknown'}",
            )

        suffix = PurePosixPath(file.filename or "file").suffix
        if not suffix:
            suffix = DEFAULT_SUFFIX_BY_CONTENT_TYPE.get(file.content_type, ".bin")
        key = f"new_photos/{uuid4().hex}{suffix}"

        try:
            s3.upload_file(file.file, key, content_type=file.content_type)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed for {file.filename or key}: {exc}",
            ) from exc

        uploaded.append(UploadedFile(filename=file.filename or key, key=key))

    count = len(uploaded)
    message = f"{count} file{'s' if count != 1 else ''} uploaded successfully."

    return UploadResponse(uploaded=uploaded, message=message)


@router.get("/download")
async def download_all_photos(_: HTTPBasicCredentials = Depends(verify_password)) -> Response:
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
