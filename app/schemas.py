from pydantic import BaseModel


class UploadedFile(BaseModel):
    filename: str
    key: str


class UploadResponse(BaseModel):
    uploaded: list[UploadedFile]
    message: str


class ErrorResponse(BaseModel):
    detail: str
