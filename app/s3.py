import io
from typing import BinaryIO

import boto3
from botocore import endpoint
from botocore.exceptions import ClientError

from app.config import settings


def _client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        endpoint_url=settings.endpoint_url,
    )


def upload_file(file_obj: BinaryIO, key: str, content_type: str | None = None) -> str:
    kwargs = {}
    if content_type:
        kwargs["ExtraArgs"] = {"ContentType": content_type}

    _client().upload_fileobj(file_obj, settings.s3_bucket_name, key, **kwargs)
    return key


def list_files() -> list[str]:
    client = _client()
    keys: list[str] = []
    paginator = client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=settings.s3_bucket_name):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])

    return keys


def download_file(key: str) -> tuple[bytes, str]:
    buffer = io.BytesIO()
    _client().download_fileobj(settings.s3_bucket_name, key, buffer)
    return buffer.getvalue(), key.split("/")[-1]


def download_all_files() -> list[tuple[bytes, str]]:
    files: list[tuple[bytes, str]] = []
    for key in list_files():
        try:
            files.append(download_file(key))
        except ClientError:
            continue
    return files
