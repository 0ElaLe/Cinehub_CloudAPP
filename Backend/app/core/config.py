from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CineHub Backend"
    environment: str = "production"
    data_mode: str = "sql"
    demo_password: str = "cinehub123"

    # CORS: lista separada por comas de orígenes permitidos.
    # Si frontend se sirve desde el mismo App Service, puede dejarse vacío.
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"

    # Azure SQL Database
    sql_host: str | None = None
    sql_port: int = 1433
    sql_database: str | None = None
    sql_user: str | None = None
    sql_password: str | None = None
    sql_odbc_driver: str = "ODBC Driver 18 for SQL Server"
    sql_trust_server_certificate: str = "no"

    # Azure Blob Storage
    blob_account_name: str | None = None
    blob_account_url: str | None = None
    blob_container_default: str = "materials"
    blob_connection_string: str | None = None

    # Límites de carga de archivos
    max_upload_mb: int = 500
    allowed_content_types: str = (
        "video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,"
        "audio/mpeg,audio/wav,audio/flac,audio/aac,"
        "image/jpeg,image/png,image/tiff,image/x-tiff,"
        "application/pdf,"
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document,"
        "application/msword,"
        "text/plain"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
