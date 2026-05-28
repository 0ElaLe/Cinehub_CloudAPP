from fastapi import UploadFile
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.core.config import settings


def get_blob_service_client() -> BlobServiceClient:
    if not settings.blob_connection_string:
        raise RuntimeError("Falta BLOB_CONNECTION_STRING en .env")

    return BlobServiceClient.from_connection_string(settings.blob_connection_string)


async def upload_material_to_blob(
    file: UploadFile,
    container_name: str,
    blob_path: str,
) -> dict:
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(container_name)

    if not container_client.exists():
        container_client.create_container()

    content = await file.read()

    blob_client = container_client.get_blob_client(blob_path)

    blob_client.upload_blob(
        content,
        overwrite=True,
        content_settings=ContentSettings(content_type=file.content_type),
    )

    return {
        "container_name": container_name,
        "blob_path": blob_path,
        "size_bytes": len(content),
        "content_type": file.content_type,
    }


def download_material_from_blob(
    container_name: str,
    blob_path: str,
) -> bytes:
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_path,
    )

    downloader = blob_client.download_blob()
    return downloader.readall()


def blob_exists(
    container_name: str,
    blob_path: str,
) -> bool:
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_path,
    )

    return blob_client.exists()
