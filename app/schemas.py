from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    key: str
    message: str


class ErrorResponse(BaseModel):
    detail: str
