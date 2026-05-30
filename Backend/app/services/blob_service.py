import logging

from fastapi import HTTPException, UploadFile, status
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_blob_service_client() -> BlobServiceClient:
    if not settings.blob_connection_string:
        raise RuntimeError(
            "Falta BLOB_CONNECTION_STRING en la configuración. "
            "Configúrala como App Setting en Azure Portal."
        )
    return BlobServiceClient.from_connection_string(settings.blob_connection_string)


def _validate_upload(file: UploadFile, content: bytes) -> None:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    allowed = {ct.strip() for ct in settings.allowed_content_types.split(",") if ct.strip()}

    if file.content_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido: '{file.content_type}'. "
                   f"Tipos aceptados: video, audio, imagen, PDF, Word, texto plano.",
        )
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {settings.max_upload_mb} MB.",
        )


async def upload_material_to_blob(
    file: UploadFile,
    container_name: str,
    blob_path: str,
) -> dict:
    content = await file.read()
    _validate_upload(file, content)

    try:
        client = get_blob_service_client()
        container_client = client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        blob_client = container_client.get_blob_client(blob_path)
        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings=ContentSettings(content_type=file.content_type),
        )
        logger.info("Blob subido: %s/%s (%d bytes)", container_name, blob_path, len(content))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "Error al subir blob '%s/%s': %s",
            container_name, blob_path, type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error al conectar con Azure Blob Storage al subir el archivo.",
        )

    return {
        "container_name": container_name,
        "blob_path": blob_path,
        "size_bytes": len(content),
        "content_type": file.content_type,
    }


def download_material_from_blob(container_name: str, blob_path: str) -> bytes:
    try:
        client = get_blob_service_client()
        blob_client = client.get_blob_client(container=container_name, blob=blob_path)
        data = blob_client.download_blob().readall()
        logger.info("Blob descargado: %s/%s (%d bytes)", container_name, blob_path, len(data))
        return data
    except Exception as exc:
        logger.error(
            "Error al descargar blob '%s/%s': %s",
            container_name, blob_path, type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error al descargar el archivo desde Azure Blob Storage.",
        )


def blob_exists(container_name: str, blob_path: str) -> bool:
    try:
        client = get_blob_service_client()
        return client.get_blob_client(container=container_name, blob=blob_path).exists()
    except Exception as exc:
        logger.warning(
            "No se pudo verificar existencia de blob '%s/%s': %s",
            container_name, blob_path, type(exc).__name__,
        )
        return False
