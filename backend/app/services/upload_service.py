import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status, UploadFile
import tempfile
import os
from PIL import Image
from typing import Optional

from ..core.config import settings


class UploadService:
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret
        )

    def validate_image(self, file: UploadFile) -> None:
        """Validate uploaded image file."""
        # Check file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size (5MB limit)
        if file.size and file.size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 5MB"
            )

    def upload_image(self, file: UploadFile, folder: str = "uploads") -> str:
        """Upload image to Cloudinary and return URL."""
        self.validate_image(file)
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
                # Write uploaded file to temporary file
                content = file.file.read()
                tmp_file.write(content)
                tmp_file.flush()
                
                # Validate with PIL
                try:
                    with Image.open(tmp_file.name) as img:
                        # Verify it's a valid image
                        img.verify()
                except Exception:
                    os.unlink(tmp_file.name)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid image file"
                    )
                
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    tmp_file.name,
                    folder=folder,
                    transformation=[
                        {"width": 400, "height": 400, "crop": "fill"},
                        {"quality": "auto", "fetch_format": "auto"}
                    ]
                )
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
                return result["secure_url"]
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )

    def delete_image(self, public_id: str) -> bool:
        """Delete image from Cloudinary."""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception:
            return False