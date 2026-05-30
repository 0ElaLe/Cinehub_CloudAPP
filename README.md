# CineHub Materials — Portal Privado de Materiales Cinematográficos

Portal interno para listar, subir y descargar materiales de producción.
Desplegado en **Azure App Service** dentro de una arquitectura **Hub and Spoke privada**.

---

## Arquitectura

```
Usuario (VPN P2S)
    │
    ▼
Hub VNet (vnet-cinehub-lab-hub)
    │  VNet Peering
    ▼
Spoke VNet (vnet-cinehub-lab-spoke-app) — 10.20.0.0/16
    │
    ├─ App Service (asp-cinehub-lab-app-01)
    │   └─ VNet Integration → tráfico privado hacia SQL y Storage
    │
    ├─ Private Endpoint SQL    (pe-cinehub-lab-sql-01)     → 10.20.2.5
    │   └─ sql-cinehub-lab-data-01.database.windows.net
    │       └─ sqldb-cinehub-lab-metadata-01
    │
    └─ Private Endpoint Blob   (pe-cinehub-lab-storage)
        └─ stcinehublabmedia01.blob.core.windows.net
            └─ contenedor: materials
```

**Stack de la aplicación:**

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python 3.11) + Uvicorn |
| Frontend | React 18 + Vite (servido por FastAPI) |
| Base de datos | Azure SQL Database via pyodbc / SQLAlchemy |
| Almacenamiento | Azure Blob Storage via azure-storage-blob |
| Secretos | Azure Key Vault (referencias en App Settings) |

---

## Despliegue en Azure App Service

### Paso 0 — Preparar la base de datos

Conecta a `sqldb-cinehub-lab-metadata-01` (via VPN o Jump host) y ejecuta los dos scripts en orden:

```sql
-- 1. Crear tablas
-- Archivo: Backend/scripts/create_schema.sql

-- 2. Insertar datos de prueba
-- Archivo: Backend/scripts/seed_data.sql
```

### Paso 1 — Configurar App Settings en Azure Portal

Ve a **App Service > asp-cinehub-lab-app-01 > Configuration > Application settings** y agrega:

| Nombre | Valor |
|---|---|
| `APP_NAME` | `CineHub Backend` |
| `ENVIRONMENT` | `production` |
| `DATA_MODE` | `sql` |
| `DEMO_PASSWORD` | `@Microsoft.KeyVault(SecretUri=https://kvcinehublabsecrets01.vault.azure.net/secrets/DEMO-PASSWORD/)` |
| `CORS_ORIGINS` | *(vacío si frontend y backend en mismo App Service)* |
| `SQL_HOST` | `sql-cinehub-lab-data-01.database.windows.net` |
| `SQL_PORT` | `1433` |
| `SQL_DATABASE` | `sqldb-cinehub-lab-metadata-01` |
| `SQL_USER` | `cinehubadmin` |
| `SQL_PASSWORD` | `@Microsoft.KeyVault(SecretUri=https://kvcinehublabsecrets01.vault.azure.net/secrets/SQL-PASSWORD/)` |
| `SQL_ODBC_DRIVER` | `ODBC Driver 18 for SQL Server` |
| `SQL_TRUST_SERVER_CERTIFICATE` | `no` |
| `BLOB_ACCOUNT_NAME` | `stcinehublabmedia01` |
| `BLOB_ACCOUNT_URL` | `https://stcinehublabmedia01.blob.core.windows.net` |
| `BLOB_CONTAINER_DEFAULT` | `materials` |
| `BLOB_CONNECTION_STRING` | `@Microsoft.KeyVault(SecretUri=https://kvcinehublabsecrets01.vault.azure.net/secrets/BLOB-CONNECTION-STRING/)` |
| `MAX_UPLOAD_MB` | `500` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `false` |

> **Key Vault**: el App Service necesita **System-Assigned Managed Identity** habilitada y una
> **Access Policy** en `kvcinehublabsecrets01` con permiso `Get` sobre Secrets.

### Paso 2 — Configurar Startup Command

En **App Service > Configuration > General settings > Startup Command**:

```
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
```

O si prefieres usar el script:

```
bash /home/site/wwwroot/startup.sh
```

### Paso 3 — Conectar GitHub via Deployment Center

1. App Service > **Deployment Center**
2. Source: **GitHub**
3. Organization / Repository: tu fork de `Cinehub_CloudAPP`
4. Branch: `main`
5. Workflow: usar el archivo `.github/workflows/azure-deploy.yml` ya incluido
6. En GitHub > Settings > Secrets, agrega:
   - `AZURE_WEBAPP_PUBLISH_PROFILE` → contenido del Publish Profile descargado desde Azure Portal

### Paso 4 — Hacer push y verificar

```bash
git add .
git commit -m "feat: configure for Azure App Service deployment"
git push origin main
```

El workflow de GitHub Actions:
1. Instala Node.js y hace `npm run build` del frontend → escribe en `Backend/static/`
2. Instala dependencias Python
3. Despliega `Backend/` al App Service

---

## Verificar la conectividad (desde VPN o Jump host)

```bash
# Estado general de la API
curl https://asp-cinehub-lab-app-01.azurewebsites.net/health

# Prueba de conexión a Azure SQL (Private Endpoint)
curl https://asp-cinehub-lab-app-01.azurewebsites.net/health/db

# Prueba de conexión a Azure Blob Storage (Private Endpoint)
curl https://asp-cinehub-lab-app-01.azurewebsites.net/health/storage

# Diagnóstico completo
curl https://asp-cinehub-lab-app-01.azurewebsites.net/health/dependencies
```

Respuesta esperada de `/health/dependencies`:

```json
{
  "api":  { "status": "ok", "environment": "production", "data_mode": "sql" },
  "sql":  { "status": "ok", "database": "sqldb-cinehub-lab-metadata-01" },
  "blob": { "status": "ok", "default_container": "materials", "default_container_exists": true }
}
```

---

## Desarrollo local

```bash
# Backend
cd Backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Copia .env.example a .env y rellena los valores reales
cp .env.example .env
uvicorn app.main:app --reload

# Frontend (en otra terminal)
cd Frontend
npm install
# Copia .env.example a .env
cp .env.example .env            # VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

Para hacer el build completo localmente (simula lo que hace CI):

```bash
cd Frontend
npm run build   # Escribe en Backend/static/

cd ../Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Abre http://127.0.0.1:8000 → sirve el frontend compilado
```

---

## Estructura del proyecto

```
Cinehub_CloudAPP/
├── .github/workflows/
│   └── azure-deploy.yml          ← GitHub Actions CI/CD
├── Backend/
│   ├── app/
│   │   ├── main.py               ← FastAPI app + sirve Frontend/static/
│   │   ├── core/config.py        ← Todas las variables de entorno
│   │   ├── db/session.py         ← Engine SQL (inicialización lazy)
│   │   ├── api/routers/
│   │   │   ├── auth.py           ← POST /auth/login, GET /auth/me
│   │   │   ├── projects.py       ← GET /projects, /projects/{id}/materials
│   │   │   ├── materials.py      ← POST /projects/{id}/materials, GET /materials/{id}/download
│   │   │   └── diagnostics.py    ← GET /health/db, /health/storage, /health/dependencies
│   │   ├── services/
│   │   │   ├── blob_service.py   ← Upload/download Azure Blob Storage
│   │   │   └── auth_service.py   ← Autenticación
│   │   └── repositories/
│   │       └── sql_repository.py ← Queries SQL
│   ├── scripts/
│   │   ├── create_schema.sql     ← CREATE TABLE (ejecutar primero)
│   │   └── seed_data.sql         ← Datos de prueba (ejecutar segundo)
│   ├── static/                   ← Frontend compilado (generado por Vite, ignorado en Git)
│   ├── requirements.txt
│   ├── startup.sh                ← Startup command para Azure App Service
│   └── .env.example              ← Referencia de App Settings
└── Frontend/
    ├── src/
    │   ├── main.jsx              ← App React (login + dashboard)
    │   ├── api.js                ← Cliente HTTP
    │   └── styles.css
    ├── vite.config.js            ← Build output → Backend/static/
    ├── package.json
    └── .env.example
```

---

## Seguridad

- Secretos manejados via **Azure Key Vault** referenciados en App Settings
- **NUNCA** committear `.env` con valores reales (está en `.gitignore`)
- Contraseñas y connection strings **no se loguean** (los errores solo exponen el tipo de excepción)
- CORS configurado vía variable de entorno `CORS_ORIGINS`
- SQL usa `Encrypt=yes` y `TrustServerCertificate=no` (TLS obligatorio)
- Toda la comunicación backend ↔ SQL/Blob va por **Private Endpoints** dentro de la VNet

### Upgrade path — Managed Identity (sin connection string)

Para eliminar `BLOB_CONNECTION_STRING` completamente, habilita Managed Identity en el App Service
y usa `DefaultAzureCredential` de `azure-identity` en `blob_service.py`:

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

credential = DefaultAzureCredential()
client = BlobServiceClient(
    account_url=settings.blob_account_url,
    credential=credential,
)
```

Esto requiere rol **Storage Blob Data Contributor** asignado a la Managed Identity del App Service
sobre la Storage Account `stcinehublabmedia01`.
