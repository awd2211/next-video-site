"""
图片上传管理 - 支持自动压缩和CDN
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import io

from app.database import get_db
from app.models.user import AdminUser
from app.utils.dependencies import get_current_admin_user
from app.utils.rate_limit import limiter, RateLimitPresets
from app.utils.minio_client import minio_client
from app.utils.image_processor import ImageProcessor

router = APIRouter()


@router.post("/upload", summary="上传图片 (自动压缩)")
async def upload_image(
    file: UploadFile = File(...),
    category: str = Form("general", description="图片分类: poster, backdrop, avatar, banner, general"),
    auto_compress: bool = Form(True, description="是否自动压缩"),
    generate_thumbnails: bool = Form(True, description="是否生成缩略图"),
    convert_webp: bool = Form(True, description="是否转换为WebP"),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    上传图片并自动处理

    功能:
    - 自动压缩大图片
    - 生成多种尺寸缩略图
    - 转换为WebP格式节省带宽
    - 上传到MinIO CDN

    返回:
    {
        "original_url": "原图URL",
        "webp_url": "WebP格式URL",
        "thumbnails": {
            "small": "小图URL",
            "medium": "中图URL",
            "large": "大图URL"
        },
        "size_saved": "节省的空间(bytes)"
    }
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )

    # 读取文件
    file_content = await file.read()
    original_size = len(file_content)
    image_file = io.BytesIO(file_content)

    # 获取图片信息
    image_info = ImageProcessor.get_image_info(image_file)

    # 生成文件名
    import uuid
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    base_name = f"{category}/{timestamp}_{unique_id}"

    result = {
        "original_url": None,
        "webp_url": None,
        "thumbnails": {},
        "size_saved": 0,
        "original_size": original_size,
        "image_info": image_info,
    }

    # 1. 处理原图 (压缩)
    if auto_compress and ImageProcessor.should_compress(image_file, threshold_mb=1.0):
        # 压缩原图
        image_file.seek(0)
        compressed = ImageProcessor.compress_image(
            image_file,
            max_size=(1920, 1080),
            quality="high",
            output_format="JPEG"
        )

        # 上传压缩后的原图
        object_name = f"{base_name}_compressed.jpg"
        original_url = minio_client.upload_image(compressed, object_name, "image/jpeg")
        result["original_url"] = original_url
        result["size_saved"] += original_size - len(compressed.getvalue())
    else:
        # 直接上传原图
        image_file.seek(0)
        ext = file.filename.split(".")[-1] if file.filename else "jpg"
        object_name = f"{base_name}.{ext}"
        original_url = minio_client.upload_image(image_file, object_name, file.content_type)
        result["original_url"] = original_url

    # 2. 转换为WebP
    if convert_webp:
        image_file.seek(0)
        webp_image = ImageProcessor.convert_to_webp(image_file, quality=85)
        webp_object_name = f"{base_name}.webp"
        webp_url = minio_client.upload_image(webp_image, webp_object_name, "image/webp")
        result["webp_url"] = webp_url
        result["size_saved"] += original_size - len(webp_image.getvalue())

    # 3. 生成缩略图
    if generate_thumbnails:
        image_file.seek(0)

        # 根据类别选择缩略图尺寸
        if category in ["poster"]:
            thumbnail_sizes = ["poster_small", "poster_medium", "poster_large"]
        else:
            thumbnail_sizes = ["small", "medium", "large"]

        thumbnails = ImageProcessor.create_thumbnails(
            image_file,
            sizes=thumbnail_sizes,
            output_format="WEBP"
        )

        # 上传缩略图
        for size_name, thumb_file in thumbnails.items():
            thumb_object_name = f"{base_name}_{size_name}.webp"
            thumb_url = minio_client.upload_image(thumb_file, thumb_object_name, "image/webp")
            result["thumbnails"][size_name] = thumb_url
            result["size_saved"] += original_size - len(thumb_file.getvalue())

    result["compression_ratio"] = f"{(result['size_saved'] / original_size * 100):.1f}%" if original_size > 0 else "0%"

    return result


@router.post("/upload-avatar", summary="上传头像 (自动裁剪为正方形)")
async def upload_avatar(
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    上传头像图片

    特点:
    - 自动裁剪为正方形
    - 生成多种尺寸 (64x64, 128x128, 256x256)
    - WebP格式
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )

    file_content = await file.read()
    image_file = io.BytesIO(file_content)

    # 打开图片并裁剪为正方形
    from PIL import Image
    img = Image.open(image_file)

    # 裁剪为正方形 (中心裁剪)
    width, height = img.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    img = img.crop((left, top, right, bottom))

    # 生成多种尺寸
    import uuid
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    base_name = f"avatars/{timestamp}_{unique_id}"

    result = {"urls": {}}

    for size in [64, 128, 256]:
        avatar_img = img.copy()
        avatar_img.thumbnail((size, size), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        avatar_img.save(output, format="WEBP", quality=90)
        output.seek(0)

        object_name = f"{base_name}_{size}.webp"
        url = minio_client.upload_image(output, object_name, "image/webp")
        result["urls"][f"{size}x{size}"] = url

    return result


@router.delete("/delete", summary="删除图片")
async def delete_image(
    object_name: str = Form(..., description="MinIO对象名称"),
    current_admin: AdminUser = Depends(get_current_admin_user),
):
    """
    从CDN删除图片
    """
    try:
        minio_client.client.remove_object(
            bucket_name=minio_client.bucket_name,
            object_name=object_name
        )
        return {"message": "删除成功", "object_name": object_name}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )
