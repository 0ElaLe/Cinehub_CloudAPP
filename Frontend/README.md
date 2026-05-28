# CineHub Frontend

Frontend sencillo para la intranet CineHub.

## Stack

- React
- Vite
- CSS plano
- Tipografía Montserrat
- Consumo de API FastAPI

## Ejecutar localmente

```bash
npm install
```

Crear `.env` a partir de `.env.example`:

```cmd
copy .env.example .env
```

Ejecutar:

```bash
npm run dev
```

Abrir:

```text
http://127.0.0.1:5173
```

## Backend esperado

Por defecto consume:

```text
http://127.0.0.1:8000
```

Puedes cambiarlo en `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Endpoints usados

```text
POST /auth/login
GET  /auth/me
GET  /projects
GET  /projects/{project_id}/materials
POST /projects/{project_id}/materials
GET  /materials/{material_id}/download
```

## Importante

El backend debe tener CORS habilitado para:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Si usas el backend FastAPI, agrega ambos orígenes en `CORSMiddleware`.
