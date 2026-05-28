# CineHub Backend - Fase 2 SQL

Esta versión conecta FastAPI con Azure SQL Database usando SQLAlchemy + pyodbc.

## Requisitos previos

1. Tener tablas creadas en Azure SQL.
2. Tener el SQL Server temporalmente accesible desde tu IP pública, si aún no hay VPN/Bastion.
3. Tener instalado Microsoft ODBC Driver 18 for SQL Server.
4. Tener variables en `.env`.

## Ejecutar

```bash
python -m venv .venv
```

CMD Windows:

```cmd
.venv\Scripts\activate.bat
```

Instalar:

```bash
pip install -r requirements.txt
```

Copiar `.env.example` a `.env` y editar contraseña/host.

Verificar drivers ODBC disponibles:

```bash
python -c "import pyodbc; print(pyodbc.drivers())"
```

Probar conexión a SQL:

```bash
python scripts/test_sql_connection.py
```

Ejecutar API:

```bash
uvicorn app.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/docs
```

## Login temporal

Mientras no tengamos `password_hash` por usuario, el login usa:

```text
email: un email existente en la tabla Usuario
password: valor de DEMO_PASSWORD
```

Ejemplo:

```text
ana.torres@cinehub.com
cinehub123
```

## Flujo de prueba

1. `POST /auth/login`
2. Copiar token.
3. Botón Authorize en Swagger.
4. Escribir `Bearer <token>`.
5. Probar `GET /projects`.
6. Probar `GET /projects/{project_id}/materials`.
7. Probar `POST /projects/{project_id}/materials`; en fase 2 simula Blob, pero inserta metadata en SQL si `DATA_MODE=sql`.
