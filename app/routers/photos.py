"""Photo Upload Router.

Handles photo upload functionality for wedding guests.
Supports multiple file uploads to NCP Object Storage.

Features:
    - Upload photos (up to 50 at once)
    - View photo list (admin only)
    - Delete photos (admin only)
    - Download photos (admin only)

Routes:
    POST /photos/upload: Upload photos
    GET /photos/api/list: Get all photos (admin only)
    DELETE /photos/api/{id}: Delete photo (admin only)
    GET /photos/api/download/{id}: Download photo (admin only)
"""

import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from app.core.database import get_db_connection, DB_TYPE
from app.database.queries import get_query
from app.core.storage import get_storage_client
from app.admin.auth import get_current_admin
import io

router = APIRouter(prefix="/photos", tags=["photos"])
logger = logging.getLogger(__name__)

# 허용되는 이미지 확장자
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.heif'}
# 최대 파일 크기 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024
# 최대 업로드 개수
MAX_UPLOAD_COUNT = 50


def validate_image_file(file: UploadFile) -> bool:
    """
    Validate uploaded image file.

    Args:
        file: Uploaded file

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If validation fails
    """
    import os

    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    return True


@router.post("/upload")
async def upload_photos(
    files: List[UploadFile] = File(...),
    uploader_name: str = Form(None)
):
    """
    Upload multiple photos.

    Args:
        files: List of image files (max 50)
        uploader_name: Name of the uploader (optional)

    Returns:
        dict: Upload result with success count and file details
    """
    if len(files) > MAX_UPLOAD_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"한 번에 최대 {MAX_UPLOAD_COUNT}장까지 업로드할 수 있습니다."
        )

    storage_client = get_storage_client()
    conn = get_db_connection()
    cursor = conn.cursor()

    uploaded_files = []
    failed_files = []

    for file in files:
        try:
            # Validate file
            validate_image_file(file)

            # Read file data
            file_data = await file.read()
            file_size = len(file_data)

            # Check file size
            if file_size > MAX_FILE_SIZE:
                failed_files.append({
                    "filename": file.filename,
                    "error": f"파일 크기가 너무 큽니다 (최대 {MAX_FILE_SIZE // (1024*1024)}MB)"
                })
                continue

            # Upload to S3 (uses default folder from env: wedding-images)
            file_path = storage_client.upload_file(
                file_data=io.BytesIO(file_data),
                filename=file.filename,
                content_type=file.content_type
            )

            # Save to database
            insert_query = get_query("photos", "insert", DB_TYPE)
            cursor.execute(insert_query, (
                file.filename,
                file_path,
                file_size,
                file.content_type,
                uploader_name
            ))

            uploaded_files.append({
                "filename": file.filename,
                "size": file_size,
                "path": file_path
            })

            logger.info(f"✅ Photo uploaded: {file.filename} by {uploader_name or 'Anonymous'}")

        except Exception as e:
            logger.error(f"❌ Failed to upload {file.filename}: {e}")
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "uploaded": len(uploaded_files),
        "failed": len(failed_files),
        "files": uploaded_files,
        "errors": failed_files
    }


@router.get("/api/list")
async def get_photos_list(
    request: Request,
    admin_user: str = Depends(get_current_admin)
):
    """
    Get list of all uploaded photos (admin only).

    Args:
        request: FastAPI request object
        admin_user: Authenticated admin username

    Returns:
        dict: List of photos with details
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    select_query = get_query("photos", "select_all")
    logger.info(f"Executing query: {select_query}")
    cursor.execute(select_query)

    photos = []
    rows = cursor.fetchall()
    logger.info(f"Found {len(rows)} photos in database")

    storage_client = get_storage_client()

    for row in rows:
        try:
            if DB_TYPE == "postgresql":
                photo = {
                    "id": row['id'],
                    "filename": row['filename'],
                    "file_path": row['file_path'],
                    "file_size": row['file_size'],
                    "content_type": row['content_type'],
                    "uploader_name": row['uploader_name'],
                    "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp'])
                }
            else:
                photo = {
                    "id": row[0],
                    "filename": row[1],
                    "file_path": row[2],
                    "file_size": row[3],
                    "content_type": row[4],
                    "uploader_name": row[5],
                    "timestamp": row[6] if len(row) > 6 else ""
                }
                if photo["timestamp"]:
                    photo["timestamp"] = photo["timestamp"].isoformat() if hasattr(photo["timestamp"], 'isoformat') else str(photo["timestamp"])

            # Generate presigned URL (valid for 1 hour)
            photo["url"] = storage_client.generate_presigned_url(photo["file_path"], expiration=3600)
            logger.info(f"Generated URL for photo {photo['id']}: {photo['url'][:50]}...")
            photos.append(photo)

        except Exception as e:
            logger.error(f"Failed to process photo: {e}")
            continue

    conn.close()

    logger.info(f"Returning {len(photos)} photos to client")
    return {
        "photos": photos,
        "total": len(photos)
    }


@router.get("/api/list-s3")
async def get_photos_from_s3(
    request: Request,
    admin_user: str = Depends(get_current_admin)
):
    """
    Get list of all photos directly from S3 bucket (admin only).

    Args:
        request: FastAPI request object
        admin_user: Authenticated admin username

    Returns:
        dict: List of photos from S3 with presigned URLs
    """
    storage_client = get_storage_client()

    # List all files in the S3 bucket's wedding-images folder
    s3_files = storage_client.list_files()

    photos = []
    for s3_file in s3_files:
        # Skip folders (objects ending with /)
        if s3_file['Key'].endswith('/'):
            continue

        try:
            # Extract filename from key
            filename = s3_file['Key'].split('/')[-1]

            # Generate presigned URL (valid for 1 hour)
            url = storage_client.generate_presigned_url(s3_file['Key'], expiration=3600)

            photo = {
                "filename": filename,
                "file_path": s3_file['Key'],
                "file_size": s3_file['Size'],
                "timestamp": s3_file['LastModified'].isoformat(),
                "url": url
            }

            photos.append(photo)

        except Exception as e:
            logger.error(f"Failed to process S3 file {s3_file.get('Key', 'unknown')}: {e}")
            continue

    # Sort by timestamp (newest first)
    photos.sort(key=lambda x: x['timestamp'], reverse=True)

    logger.info(f"Returning {len(photos)} photos from S3 bucket")
    return {
        "photos": photos,
        "total": len(photos)
    }


@router.delete("/api/{photo_id}")
async def delete_photo(
    photo_id: int,
    request: Request,
    admin_user: str = Depends(get_current_admin)
):
    """
    Delete a photo (admin only).

    Args:
        photo_id: ID of the photo to delete
        request: FastAPI request object
        admin_user: Authenticated admin username

    Returns:
        dict: Deletion result
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get photo info first
    select_query = get_query("photos", "select_by_id", DB_TYPE)
    cursor.execute(select_query, (photo_id,))
    photo = cursor.fetchone()

    if not photo:
        conn.close()
        raise HTTPException(status_code=404, detail="사진을 찾을 수 없습니다.")

    # Get file path
    if DB_TYPE == "postgresql":
        file_path = photo['file_path']
    else:
        file_path = photo[2]

    # Delete from storage
    storage_client = get_storage_client()
    storage_client.delete_file(file_path)

    # Delete from database
    delete_query = get_query("photos", "delete", DB_TYPE)
    cursor.execute(delete_query, (photo_id,))

    conn.commit()
    conn.close()

    logger.info(f"✅ Photo deleted: {photo_id} by admin {admin_user}")

    return {
        "status": "success",
        "message": "사진이 삭제되었습니다."
    }


@router.get("/api/download/{photo_id}")
async def download_photo(
    photo_id: int,
    request: Request,
    admin_user: str = Depends(get_current_admin)
):
    """
    Download a photo (admin only).

    Args:
        photo_id: ID of the photo to download
        request: FastAPI request object
        admin_user: Authenticated admin username

    Returns:
        StreamingResponse: Photo file
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get photo info
    select_query = get_query("photos", "select_by_id", DB_TYPE)
    cursor.execute(select_query, (photo_id,))
    photo = cursor.fetchone()

    if not photo:
        conn.close()
        raise HTTPException(status_code=404, detail="사진을 찾을 수 없습니다.")

    # Get photo details
    if DB_TYPE == "postgresql":
        file_path = photo['file_path']
        filename = photo['filename']
        content_type = photo['content_type']
    else:
        file_path = photo[2]
        filename = photo[1]
        content_type = photo[4]

    conn.close()

    # Get presigned URL and redirect
    storage_client = get_storage_client()
    download_url = storage_client.generate_presigned_url(file_path, expiration=300)  # 5 minutes

    if not download_url:
        raise HTTPException(status_code=500, detail="다운로드 URL 생성에 실패했습니다.")

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=download_url)


@router.get("/api/download-s3/{file_path:path}")
async def download_photo_from_s3(
    file_path: str,
    request: Request,
    admin_user: str = Depends(get_current_admin)
):
    """
    Download a photo directly from S3 bucket (admin only).

    Args:
        file_path: S3 file path (key)
        request: FastAPI request object
        admin_user: Authenticated admin username

    Returns:
        RedirectResponse: Redirect to presigned S3 URL
    """
    storage_client = get_storage_client()

    # Generate presigned URL for download (valid for 5 minutes)
    download_url = storage_client.generate_presigned_url(file_path, expiration=300)

    if not download_url:
        raise HTTPException(status_code=500, detail="다운로드 URL 생성에 실패했습니다.")

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=download_url)


@router.delete("/api/delete-s3/{file_path:path}")
async def delete_photo_from_s3(
    file_path: str,
    request: Request,
    admin_user: str = Depends(get_current_admin)
):
    """
    Delete a photo directly from S3 bucket (admin only).

    Args:
        file_path: S3 file path (key)
        request: FastAPI request object
        admin_user: Authenticated admin username

    Returns:
        dict: Deletion result
    """
    storage_client = get_storage_client()

    # Delete from S3
    success = storage_client.delete_file(file_path)

    if not success:
        raise HTTPException(status_code=500, detail="사진 삭제에 실패했습니다.")

    logger.info(f"✅ Photo deleted from S3: {file_path} by admin {admin_user}")

    return {
        "status": "success",
        "message": "사진이 삭제되었습니다."
    }


@router.get("/api/stats")
async def get_photos_stats(
    request: Request,
    admin_user: str = Depends(get_current_admin)
):
    """
    Get photo statistics (admin only).

    Args:
        request: FastAPI request object
        admin_user: Authenticated admin username

    Returns:
        dict: Photo statistics
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    count_query = get_query("photos", "count_all")
    cursor.execute(count_query)
    result = cursor.fetchone()

    if DB_TYPE == "postgresql":
        total_count = result['count'] if result else 0
    else:
        total_count = result[0] if result else 0

    # Get total file size
    cursor.execute("SELECT SUM(file_size) FROM photos")
    size_result = cursor.fetchone()

    if DB_TYPE == "postgresql":
        total_size = size_result['sum'] if size_result and size_result['sum'] else 0
    else:
        total_size = size_result[0] if size_result and size_result[0] else 0

    conn.close()

    return {
        "total_photos": total_count,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }
