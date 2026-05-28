from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CineHub Backend"
    environment: str = "local"
    data_mode: str = "mock"
    demo_password: str = "cinehub123"

    sql_host: str | None = None
    sql_port: int = 1433
    sql_database: str | None = None
    sql_user: str | None = None
    sql_password: str | None = None
    sql_odbc_driver: str = "ODBC Driver 18 for SQL Server"
    sql_trust_server_certificate: str = "no"

    blob_account_name: str | None = None
    blob_account_url: str | None = None
    blob_container_default: str = "materials"
    blob_connection_string: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
