# Guía para el equipo App Spoke: App Service, Key Vault y conexión privada con Data Spoke

## 1. Objetivo

Esta guía reúne la información que necesita el equipo encargado del **spoke de aplicación** para desplegar CineHub en Azure App Service, conectar el backend con Azure SQL Database y Blob Storage del dominio de datos, usar Azure Key Vault para secretos y mantener la comunicación privada mediante VNet Integration, Private Endpoints, Private DNS y, si aplica, VNet Peering.

La arquitectura lógica esperada es:

```text
Usuario interno
  → VPN P2S / red privada
  → App Service privado
  → Backend FastAPI
  → Azure SQL Database privado
  → Azure Blob Storage privado
  → Azure Key Vault para secretos
```

---

## 2. Respuesta corta: ¿hay que cambiar el código?

### 2.1 Para conectarse desde App Spoke hacia Data Spoke

**No debería requerirse cambio de código** si el backend ya usa variables de entorno y FQDNs normales de Azure.

El código puede seguir usando valores como:

```env
SQL_HOST=sql-cinehub-lab-data-01.database.windows.net
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
```

Con Private DNS correctamente configurado, esos nombres se resuelven a IPs privadas desde la red de la aplicación. Por tanto, la lógica de Python no necesita saber si SQL y Storage están en otra VNet, otra subnet o detrás de un Private Endpoint.

Lo que sí debe existir a nivel infraestructura:

```text
App Service
  → VNet Integration hacia una subnet del App Spoke
  → Peering App Spoke ↔ Data Spoke, si son VNets separadas
  → Private DNS zones vinculadas a la VNet usada por la app
  → Private Endpoints de SQL, Blob y Key Vault, si aplica
```

### 2.2 Para Key Vault

**No se requiere cambio de código** si se usan **Key Vault References** en App Service.

El backend seguirá leyendo:

```python
settings.sql_password
settings.blob_connection_string
settings.demo_password
```

pero en Azure App Service esos valores vendrán de Key Vault mediante referencias como:

```text
@Microsoft.KeyVault(SecretUri=https://kv-cinehub-lab-data-01.vault.azure.net/secrets/SQL-PASSWORD/<version>)
```

### 2.3 Cuándo sí habría cambio de código

Sí habría cambios de código si se decide:

1. Leer Key Vault directamente desde Python con el SDK.
2. Conectarse a Blob Storage con Managed Identity en vez de connection string.
3. Conectarse a Azure SQL con Microsoft Entra ID en vez de usuario/contraseña SQL.
4. Reemplazar el login temporal por JWT real o Microsoft Entra ID.

Para esta práctica, la opción recomendada es **no modificar el código para Key Vault** y usar Key Vault References desde App Service.

---

## 3. Dos escenarios de red posibles

### Escenario A: App Spoke y Data Spoke como VNets separadas

```text
Hub VNet
 ├── VPN Gateway
 ├── Bastion
 └── Peering con App/Data

App Spoke VNet
 ├── Subnet para VNet Integration del App Service
 ├── Subnet para Private Endpoint del App Service
 └── App Service Plan + App Service

Data Spoke VNet
 ├── Subnet de Private Endpoints
 ├── Private Endpoint SQL
 ├── Private Endpoint Blob
 ├── Private Endpoint Key Vault, opcional
 ├── Azure SQL Database
 ├── Storage Account
 └── Key Vault
```

En este caso se necesita **VNet Peering App ↔ Data**.

### Escenario B: una sola VNet de workloads segmentada por subnets

```text
Hub VNet
  ↕ Peering
VNet Workloads
 ├── snet-app-integration
 ├── snet-app-private-endpoint
 ├── snet-data-private-endpoints
 ├── snet-data-storage
 └── snet-data-sql
```

En este caso no hay peering App/Data porque todo vive dentro de la misma VNet. La separación es por subnets.

Frase recomendada para documentarlo:

> Por alcance de laboratorio, el spoke de workloads se segmenta por subredes funcionales. La aplicación usa una subnet de integración para tráfico saliente y los recursos de datos se exponen mediante Private Endpoints en una subnet dedicada.

---

## 4. Componentes del equipo App

| Recurso | Nombre sugerido | Función |
|---|---|---|
| App Service Plan | `asp-cinehub-lab-app-01` | Hospeda backend/frontend. |
| App Service API | `app-cinehub-lab-api-01` | Backend FastAPI. |
| App Service Frontend | `app-cinehub-lab-web-01` | Frontend React, si se despliega separado. |
| Subnet integración | `snet-cinehub-lab-app-integration-01` | Salida privada del App Service hacia VNets. |
| Subnet Private Endpoint App | `snet-cinehub-lab-app-pe-01` | Entrada privada hacia App Service. |
| Private Endpoint App | `pe-cinehub-lab-app-01` | Acceso privado a la app. |
| DNS privado App Service | `privatelink.azurewebsites.net` | Resolución privada de la app. |

Tags mínimos:

```text
Project=CineHub
Environment=Lab
Owner=EquipoApp
CostCenter=CloudClass
Workload=AppPrivate
```

---

## 5. App Service: entrada privada vs salida privada

### 5.1 VNet Integration

**VNet Integration sirve para tráfico saliente** desde App Service hacia recursos dentro de una VNet o redes peered.

Se necesita para que el backend pueda llamar a:

```text
Azure SQL Database privado
Blob Storage privado
Key Vault privado, si aplica
```

### 5.2 Private Endpoint para App Service

**Private Endpoint para App Service sirve para tráfico entrante** hacia la app desde una red privada.

Se necesita si la aplicación no debe estar pública en internet.

### 5.3 Conclusión

```text
VNet Integration = salida privada desde la app hacia SQL/Storage/Key Vault
Private Endpoint de App Service = entrada privada de usuarios hacia la app
```

No son lo mismo. Se complementan.

---

## 6. Subnets necesarias para App Service

Se recomienda usar subnets separadas.

```text
snet-cinehub-lab-app-integration-01
  Uso: VNet Integration del App Service.
  Debe estar delegada a Microsoft.Web/serverFarms.

snet-cinehub-lab-app-pe-01
  Uso: Private Endpoint del App Service.
  No debe ser la misma subnet de VNet Integration.
```

No usar la misma subnet para VNet Integration y Private Endpoint de App Service.

---

## 7. DNS privado necesario

### Para Azure SQL

Zona:

```text
privatelink.database.windows.net
```

Debe resolver:

```text
sql-cinehub-lab-data-01.database.windows.net
```

hacia la IP privada del Private Endpoint de SQL.

### Para Blob Storage

Zona:

```text
privatelink.blob.core.windows.net
```

Debe resolver:

```text
stcinehublabdata01.blob.core.windows.net
```

hacia la IP privada del Private Endpoint de Blob.

### Para App Service privado

Zona:

```text
privatelink.azurewebsites.net
```

Debe resolver:

```text
app-cinehub-lab-api-01.azurewebsites.net
```

hacia la IP privada del Private Endpoint de App Service.

### Para Key Vault privado, si aplica

Zona:

```text
privatelink.vaultcore.azure.net
```

Debe resolver:

```text
kv-cinehub-lab-data-01.vault.azure.net
```

hacia la IP privada del Private Endpoint de Key Vault.

### VNet links

Si App y Data son VNets separadas:

```text
privatelink.database.windows.net  → link a App VNet y Data VNet
privatelink.blob.core.windows.net → link a App VNet y Data VNet
privatelink.azurewebsites.net     → link a Hub/App VNet según desde dónde entren los usuarios
privatelink.vaultcore.azure.net   → link a App VNet si Key Vault está privado
```

Si solo existe una VNet de workloads:

```text
Cada Private DNS Zone se vincula a la VNet de workloads.
```

---

## 8. Configuración de App Service para backend FastAPI

### 8.1 App Service Plan

Usar Linux App Service Plan compatible con Python.

Recomendación para laboratorio:

```text
Tier: Basic, Standard o Premium pequeño
Runtime: Python 3.11 o 3.12
OS: Linux
```

Si se requiere Private Endpoint o VNet Integration, revisar que el SKU elegido lo soporte.

### 8.2 App Service para API

Nombre sugerido:

```text
app-cinehub-lab-api-01
```

Runtime:

```text
Python 3.11
```

Startup command sugerido:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Si App Service no enruta correctamente al puerto, agregar en App Settings:

```text
WEBSITES_PORT=8000
```

### 8.3 Nota importante sobre `pyodbc`

El backend actual usa:

```text
SQLAlchemy + pyodbc + ODBC Driver for SQL Server
```

En local funcionó porque la laptop tiene instalado:

```text
ODBC Driver 17 for SQL Server
```

En App Service Linux puede ocurrir que el driver ODBC no esté disponible en el entorno base. Si aparece un error parecido a:

```text
Can't open lib 'ODBC Driver 17 for SQL Server'
```

hay dos caminos:

1. Usar un **custom container** en App Service con el ODBC Driver instalado.
2. Ajustar el backend para usar otra librería compatible con Azure SQL.

El equipo App debe validar este punto temprano usando:

```text
GET /health/dependencies
```

---

## 9. Variables de entorno del backend

El código actual lee variables de entorno. En App Service se configuran en:

```text
App Service
→ Settings
→ Environment variables
→ App settings
```

Variables requeridas:

```text
APP_NAME=CineHub Backend
ENVIRONMENT=azure
DATA_MODE=sql

DEMO_PASSWORD=<desde Key Vault>

SQL_HOST=sql-cinehub-lab-data-01.database.windows.net
SQL_PORT=1433
SQL_DATABASE=sqldb-cinehub-lab-metadata-01
SQL_USER=cinehubadmin
SQL_PASSWORD=<desde Key Vault>
SQL_ODBC_DRIVER=ODBC Driver 17 for SQL Server
SQL_TRUST_SERVER_CERTIFICATE=no

BLOB_ACCOUNT_NAME=stcinehublabdata01
BLOB_ACCOUNT_URL=https://stcinehublabdata01.blob.core.windows.net
BLOB_CONTAINER_DEFAULT=materials
BLOB_CONNECTION_STRING=<desde Key Vault>
```

---

## 10. Key Vault: estrategia recomendada

### 10.1 No modificar código

La aplicación seguirá leyendo variables de entorno.

En App Service, las variables sensibles usarán referencias a Key Vault.

### 10.2 Secretos en Key Vault

Crear estos secretos:

```text
SQL-PASSWORD
BLOB-CONNECTION-STRING
DEMO-PASSWORD
```

Opcionalmente también se pueden guardar:

```text
SQL-USER
SQL-HOST
SQL-DATABASE
```

pero lo esencial es no exponer contraseñas ni connection strings.

### 10.3 App Settings con Key Vault References

Ejemplo:

```text
SQL_PASSWORD=@Microsoft.KeyVault(SecretUri=https://kv-cinehub-lab-data-01.vault.azure.net/secrets/SQL-PASSWORD/<version>)

BLOB_CONNECTION_STRING=@Microsoft.KeyVault(SecretUri=https://kv-cinehub-lab-data-01.vault.azure.net/secrets/BLOB-CONNECTION-STRING/<version>)

DEMO_PASSWORD=@Microsoft.KeyVault(SecretUri=https://kv-cinehub-lab-data-01.vault.azure.net/secrets/DEMO-PASSWORD/<version>)
```

El resto puede ir como texto normal:

```text
SQL_HOST=sql-cinehub-lab-data-01.database.windows.net
SQL_PORT=1433
SQL_DATABASE=sqldb-cinehub-lab-metadata-01
SQL_USER=cinehubadmin
BLOB_ACCOUNT_NAME=stcinehublabdata01
BLOB_CONTAINER_DEFAULT=materials
```

### 10.4 Managed Identity

Activar identidad administrada:

```text
App Service
→ Identity
→ System assigned
→ On
→ Save
```

Después dar permisos en Key Vault.

Si Key Vault usa Azure RBAC:

```text
Key Vault
→ Access control (IAM)
→ Add role assignment
→ Role: Key Vault Secrets User
→ Assign access to: Managed identity
→ Select: app-cinehub-lab-api-01
```

Si Key Vault usa Access Policies:

```text
Key Vault
→ Access policies
→ Create
→ Secret permissions: Get, List
→ Principal: identidad administrada del App Service
```

---

## 11. Si Key Vault también es privado

Si Key Vault tiene Private Endpoint y public access deshabilitado, entonces App Service debe poder llegar al Private Endpoint del vault.

Requisitos:

```text
1. App Service con VNet Integration.
2. Private DNS Zone de Key Vault vinculada a la VNet de la app.
3. Ruta desde App Spoke hacia Data/KeyVault Spoke.
4. Permisos RBAC o Access Policy.
```

Zona DNS de Key Vault:

```text
privatelink.vaultcore.azure.net
```

Si App Service no puede resolver o alcanzar Key Vault, las App Settings con referencias a Key Vault no se resolverán correctamente.

Para Linux App Service, si hay problemas de salida privada hacia Key Vault, revisar la configuración de enrutamiento de VNet Integration y habilitar route all si es necesario.

---

## 12. VNet Integration del backend

Ruta en portal:

```text
App Service
→ Networking
→ VNet Integration
→ Add VNet
```

Seleccionar:

```text
VNet: App Spoke VNet
Subnet: snet-cinehub-lab-app-integration-01
```

La subnet de integración debe estar dedicada/delegada.

Si App y Data son VNets separadas:

```text
App VNet ↔ Data VNet
```

deben estar peered.

Configuración de peering:

```text
Allow virtual network access: Enabled
Allow forwarded traffic: según diseño; normalmente no necesario para acceso directo a Private Endpoints
Use remote gateways: según diseño de Hub/VPN
Allow gateway transit: en Hub, si aplica
```

---

## 13. Private Endpoint del App Service

Para que la app no sea pública:

```text
App Service
→ Networking
→ Private endpoint connections
→ Create
```

Configuración sugerida:

```text
Name: pe-cinehub-lab-api-01
VNet: App Spoke VNet o Workloads VNet
Subnet: snet-cinehub-lab-app-pe-01
Private DNS integration: Yes
Private DNS zone: privatelink.azurewebsites.net
```

Después de validar acceso privado:

```text
App Service
→ Networking
→ Public network access
→ Disabled
```

Si aún necesitan entrar desde internet para pruebas, pueden dejar acceso público restringido temporalmente, pero la evidencia final debe mostrar acceso privado.

---

## 14. Conectividad con Data Spoke

El backend debe llegar a:

```text
SQL:       sql-cinehub-lab-data-01.database.windows.net:1433
Blob:      stcinehublabdata01.blob.core.windows.net:443
Key Vault: kv-cinehub-lab-data-01.vault.azure.net:443
```

Con Private DNS, esos nombres deben resolver a IPs privadas.

No usar IPs en el código ni en App Settings.

### Pruebas recomendadas

Endpoint principal:

```text
GET /health/dependencies
```

Respuesta esperada:

```json
{
  "api": {
    "status": "ok"
  },
  "sql": {
    "status": "ok"
  },
  "blob": {
    "status": "ok"
  }
}
```

Si falla SQL:

```text
Revisar VNet Integration, peering, DNS de privatelink.database.windows.net, firewall/Public network access de SQL y credenciales.
```

Si falla Blob:

```text
Revisar BLOB_CONNECTION_STRING, Storage firewall, Private Endpoint Blob, DNS de privatelink.blob.core.windows.net y permisos.
```

Si falla Key Vault reference:

```text
Revisar Managed Identity, rol Key Vault Secrets User, Access Policies, Private Endpoint de Key Vault y DNS privatelink.vaultcore.azure.net.
```

---

## 15. Storage Account: punto de atención

El backend actual usa:

```text
BLOB_CONNECTION_STRING
```

Eso implica uso de Storage Account Key. Por tanto:

```text
Allow storage account key access = Enabled
```

Si se deshabilita el acceso por keys, el connection string dejará de funcionar.

Mejora futura:

```text
Cambiar código para usar Managed Identity + Storage Blob Data Contributor.
```

Eso sería más seguro, pero sí implica cambio de código.

---

## 16. GitHub y despliegue

### 16.1 Repositorio

No subir:

```text
.env
.venv/
__pycache__/
node_modules/
dist/
```

Subir:

```text
.env.example
requirements.txt
app/
scripts/
README.md
```

### 16.2 Deployment Center

En App Service:

```text
Deployment Center
→ Source: GitHub
→ Repository: cinehub
→ Branch: main
→ Workflow: GitHub Actions
```

Revisar que el workflow instale dependencias:

```bash
pip install -r requirements.txt
```

y que el App Service tenga startup command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 16.3 Variables de entorno

Después del despliegue, configurar App Settings antes de probar la app.

Cada cambio en App Settings reinicia la app.

---

## 17. Frontend

Si frontend y backend están separados:

```text
Frontend App Service:
app-cinehub-lab-web-01

Backend App Service:
app-cinehub-lab-api-01
```

El frontend debe tener:

```text
VITE_API_BASE_URL=https://app-cinehub-lab-api-01.azurewebsites.net
```

Si el backend es privado mediante Private Endpoint, el frontend también debe estar dentro de la red privada o ser servido desde un entorno que pueda resolver y alcanzar el endpoint privado.

Para laboratorio, también se puede servir frontend y backend juntos, pero separarlos facilita el diseño.

### CORS

En backend FastAPI, agregar origen del frontend:

```python
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://app-cinehub-lab-web-01.azurewebsites.net"
]
```

Si el backend es privado y solo lo consume el frontend privado, CORS sigue siendo necesario si son dominios diferentes.

---

## 18. Evidencias para la entrega

El equipo App debería capturar:

```text
1. App Service Plan creado.
2. App Service backend creado.
3. GitHub Deployment Center / GitHub Actions funcionando.
4. App Settings configuradas.
5. Key Vault references en App Settings.
6. Managed Identity activada.
7. Rol Key Vault Secrets User asignado.
8. VNet Integration configurada.
9. Private Endpoint del App Service creado.
10. Private DNS Zone privatelink.azurewebsites.net con registro A.
11. Public network access disabled en App Service.
12. /health funcionando.
13. /health/dependencies mostrando sql=ok y blob=ok.
14. Login funcionando.
15. Listado de proyectos.
16. Subida de material.
17. Blob creado en Storage.
18. Metadata creada en SQL.
19. Descarga funcionando.
```

---

## 19. Checklist operativo del equipo App

### Antes del despliegue

```text
[ ] Backend probado localmente.
[ ] Frontend probado localmente.
[ ] .env fuera de GitHub.
[ ] CORS incluye URL local y URL Azure.
[ ] /health/dependencies funciona localmente.
```

### App Service

```text
[ ] App Service Plan creado.
[ ] App Service API creado.
[ ] Runtime Python configurado.
[ ] Startup command configurado.
[ ] GitHub deployment configurado.
[ ] Variables de entorno configuradas.
[ ] Key Vault references configuradas.
[ ] Managed Identity activada.
[ ] Permisos a Key Vault asignados.
```

### Red

```text
[ ] VNet Integration activa.
[ ] Subnet de integración correcta.
[ ] Peering App ↔ Data validado, si aplica.
[ ] Private DNS SQL vinculado a App VNet.
[ ] Private DNS Blob vinculado a App VNet.
[ ] Private DNS Key Vault vinculado a App VNet, si aplica.
[ ] Private Endpoint App creado.
[ ] Public network access disabled en la app, si ya está validado.
```

### Validación funcional

```text
[ ] GET /health
[ ] GET /health/dependencies
[ ] POST /auth/login
[ ] GET /projects
[ ] GET /projects/{id}/materials
[ ] POST /projects/{id}/materials
[ ] GET /materials/{id}/download
```

---

## 20. Resumen para defensa

La aplicación se despliega en Azure App Service como servicio PaaS. El backend no almacena secretos en el código ni en el repositorio; las credenciales sensibles se referencian desde Azure Key Vault mediante App Settings y la identidad administrada del App Service. La comunicación hacia Azure SQL Database y Blob Storage se realiza usando los nombres FQDN normales de Azure, pero gracias a Private DNS esos nombres resuelven a Private Endpoints dentro del entorno privado. La conectividad saliente se habilita mediante VNet Integration y, si App y Data son VNets separadas, mediante VNet Peering. Para el acceso entrante privado hacia la app se usa un Private Endpoint de App Service y se deshabilita el acceso público una vez validada la solución.

---

## 21. Fuentes oficiales recomendadas

- App Service VNet Integration: https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration
- App Service Private Endpoint: https://learn.microsoft.com/en-us/azure/app-service/overview-private-endpoint
- App Service App Settings: https://learn.microsoft.com/en-us/azure/app-service/configure-common
- Key Vault references en App Service: https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references
- Managed Identity en App Service: https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity
- Private DNS para Private Endpoints: https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns
- Key Vault con Private Link: https://learn.microsoft.com/en-us/azure/key-vault/general/private-link-service
