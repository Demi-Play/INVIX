from datetime import timedelta
from functools import lru_cache
from io import BytesIO

from minio import Minio

from .settings import settings


# minio-клиенты
def build_client(endpoint: str) -> Minio:
    if not settings.minio_access_key or not settings.minio_secret_key:
        raise RuntimeError("MINIO_ACCESS_KEY и MINIO_SECRET_KEY должны быть заданы")
    return Minio(
        endpoint=endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        region=settings.minio_region,
    )


@lru_cache
def get_client() -> Minio:
    """Клиент для работы с хранилищем из backend (внутренний endpoint)."""
    return build_client(settings.minio_endpoint)


@lru_cache
def get_public_client() -> Minio:
    """Клиент для подписи URL, которые открывает браузер (публичный endpoint)."""
    return build_client(settings.minio_public_endpoint)


def bucket_exists() -> bool:
    return get_client().bucket_exists(settings.minio_bucket)


def upload_object(
    object_name: str, data: bytes, content_type: str = "application/octet-stream"
) -> None:
    client = get_client()
    client.put_object(
        bucket_name=settings.minio_bucket,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def presigned_url(object_name: str, expires: timedelta | None = None) -> str:
    if expires is None:
        expires = timedelta(seconds=settings.minio_presign_expires_seconds)
    return get_public_client().presigned_get_object(
        settings.minio_bucket,
        object_name,
        expires=expires,
    )
