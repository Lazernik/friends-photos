from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router

import sys
import boto3
import botocore
import certifi
import os

print(sys.version)
print(boto3.__version__)
print(botocore.__version__)
print(certifi.where())
print(os.environ.get("AWS_CA_BUNDLE"))

app = FastAPI(title="Friends Photos", version="1.0.0")
app.include_router(router, prefix="/api")

static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
