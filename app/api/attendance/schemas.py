from typing import Optional
from fastapi import File, UploadFile
from pydantic import BaseModel


class UploadFileSchema(BaseModel):
    batch_name: str
    year_name: str
    section_name: str

    class Config:
        from_attributes = True