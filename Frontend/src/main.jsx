import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Download,
  FileAudio,
  FileImage,
  FileText,
  FileVideo,
  Film,
  LogOut,
  Plus,
  RefreshCcw,
  ShieldCheck,
  Upload,
} from "lucide-react";
import {
  API_BASE_URL,
  downloadMaterial,
  getMe,
  getProjectMaterials,
  getProjects,
  login,
  uploadMaterial,
} from "./api";
import "./styles.css";

const MATERIAL_TYPES = ["Video", "Audio", "Imagen", "LUT", "Guion", "Subtitulo", "Documento", "Otro"];
const CONFIDENTIALITY_LEVELS = ["Interno", "Confidencial", "Restringido"];

function materialIcon(type) {
  const normalized = (type || "").toLowerCase();

  if (normalized.includes("video")) return <FileVideo size={24} />;
  if (normalized.includes("audio")) return <FileAudio size={24} />;
  if (normalized.includes("imagen")) return <FileImage size={24} />;
  if (normalized.includes("guion") || normalized.includes("documento") || normalized.includes("subtitulo")) {
    return <FileText size={24} />;
  }

  return <Film size={24} />;
}

function formatDate(value) {
  if (!value) return "Sin fecha";
  try {
    return new Intl.DateTimeFormat("es-MX", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("ana.torres@cinehub.com");
  const [password, setPassword] = useState("cinehub123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await login(email, password);
      localStorage.setItem("cinehub_token", data.access_token);
      await onLogin();
    } catch (err) {
      setError(err.message || "No se pudo iniciar sesión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-layout">
      <section className="login-card">
        <div className="logo-placeholder">
          <Film size={34} />
          <span>Logo</span>
        </div>

        <div className="login-heading">
          <p className="eyebrow">Intranet privada</p>
          <h1>CineHub Materials</h1>
          <p>
            Acceso seguro para equipos de edición, color, audio y producción.
          </p>
        </div>

        <form className="form-stack" onSubmit={handleSubmit}>
          <label>
            Correo
            <input
              type="email"
              value={email}
              autoComplete="username"
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>

          <label>
            Contraseña
            <input
              type="password"
              value={password}
              autoComplete="current-password"
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          {error && <div className="error-box">{error}</div>}

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Entrando..." : "Iniciar sesión"}
          </button>
        </form>

        <p className="api-hint">API: {API_BASE_URL}</p>
      </section>
    </main>
  );
}

function AppHeader({ user, onLogout }) {
  return (
    <header className="app-header">
      <div className="brand-block">
        <div className="brand-logo">
          <Film size={25} />
        </div>
        <div>
          <p className="eyebrow">CineHub</p>
          <h1>Materials Workspace</h1>
        </div>
      </div>

      <div className="user-block">
        <div>
          <strong>{user?.nombres} {user?.apellidos}</strong>
          <span>{user?.email}</span>
        </div>
        <button className="ghost-button" onClick={onLogout}>
          <LogOut size={18} />
          Salir
        </button>
      </div>
    </header>
  );
}

function ProjectSelector({ projects, selectedProjectId, onSelect }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Proyectos</p>
          <h2>Selecciona un proyecto</h2>
        </div>
      </div>

      <select
        className="project-select"
        value={selectedProjectId || ""}
        onChange={(event) => onSelect(Number(event.target.value))}
      >
        <option value="" disabled>
          Selecciona...
        </option>
        {projects.map((project) => (
          <option key={project.proyecto_id} value={project.proyecto_id}>
            {project.nombre}
          </option>
        ))}
      </select>

      {projects.length === 0 && (
        <p className="muted">No hay proyectos disponibles para este usuario.</p>
      )}
    </section>
  );
}

function MaterialCard({ material, onDownload }) {
  return (
    <article className="material-card">
      <div className="material-icon">
        {materialIcon(material.tipo_material)}
      </div>

      <div className="material-content">
        <div className="material-title-row">
          <h3>{material.nombre}</h3>
          <span className={`badge ${material.nivel_confidencialidad?.toLowerCase()}`}>
            {material.nivel_confidencialidad}
          </span>
        </div>

        <div className="metadata-grid">
          <span><strong>Tipo:</strong> {material.tipo_material}</span>
          <span><strong>Versión:</strong> {material.version}</span>
          <span><strong>Contenedor:</strong> {material.container_name}</span>
          <span><strong>Fecha:</strong> {formatDate(material.fecha_creacion)}</span>
        </div>

        <p className="blob-path">{material.blob_path}</p>
      </div>

      <button className="download-button" onClick={() => onDownload(material)}>
        <Download size={18} />
        Descargar
      </button>
    </article>
  );
}

function UploadForm({ projectId, onUploaded }) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [tipoMaterial, setTipoMaterial] = useState("Video");
  const [version, setVersion] = useState("v1");
  const [containerName, setContainerName] = useState("materials");
  const [confidentiality, setConfidentiality] = useState("Interno");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    if (!file) {
      setMessage("Selecciona un archivo.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      await uploadMaterial(projectId, {
        file,
        tipo_material: tipoMaterial,
        version,
        container_name: containerName,
        nivel_confidencialidad: confidentiality,
      });

      setMessage("Material subido correctamente.");
      setFile(null);
      setVersion("v1");
      await onUploaded();
    } catch (err) {
      setMessage(err.message || "No se pudo subir el material.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel upload-panel">
      <button className="primary-button" onClick={() => setOpen((value) => !value)}>
        <Plus size={18} />
        {open ? "Cerrar formulario" : "Subir nuevo material"}
      </button>

      {open && (
        <form className="upload-form" onSubmit={handleSubmit}>
          <label>
            Archivo
            <input
              type="file"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
          </label>

          <div className="form-grid">
            <label>
              Tipo de material
              <select value={tipoMaterial} onChange={(event) => setTipoMaterial(event.target.value)}>
                {MATERIAL_TYPES.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </label>

            <label>
              Versión
              <input
                value={version}
                onChange={(event) => setVersion(event.target.value)}
                placeholder="v1"
              />
            </label>

            <label>
              Contenedor
              <input
                value={containerName}
                onChange={(event) => setContainerName(event.target.value)}
                placeholder="materials"
              />
            </label>

            <label>
              Confidencialidad
              <select
                value={confidentiality}
                onChange={(event) => setConfidentiality(event.target.value)}
              >
                {CONFIDENTIALITY_LEVELS.map((level) => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </label>
          </div>

          {message && <div className="info-box">{message}</div>}

          <button className="primary-button" type="submit" disabled={loading}>
            <Upload size={18} />
            {loading ? "Subiendo..." : "Guardar material"}
          </button>
        </form>
      )}
    </section>
  );
}

function Dashboard() {
  const [user, setUser] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [loadingMaterials, setLoadingMaterials] = useState(false);
  const [error, setError] = useState("");

  const selectedProject = useMemo(
    () => projects.find((project) => project.proyecto_id === selectedProjectId),
    [projects, selectedProjectId]
  );

  async function loadInitialData() {
    setError("");
    const [me, projectList] = await Promise.all([getMe(), getProjects()]);
    setUser(me);
    setProjects(projectList);

    if (projectList.length > 0) {
      setSelectedProjectId(projectList[0].proyecto_id);
    }
  }

  async function loadMaterials(projectId = selectedProjectId) {
    if (!projectId) return;
    setLoadingMaterials(true);
    setError("");

    try {
      const materialList = await getProjectMaterials(projectId);
      setMaterials(materialList);
    } catch (err) {
      setError(err.message || "No se pudieron cargar los materiales.");
    } finally {
      setLoadingMaterials(false);
    }
  }

  async function handleDownload(material) {
    setError("");
    try {
      await downloadMaterial(material);
      await loadMaterials();
    } catch (err) {
      setError(err.message || "No se pudo descargar el material.");
    }
  }

  function handleLogout() {
    localStorage.removeItem("cinehub_token");
    window.location.reload();
  }

  useEffect(() => {
    loadInitialData().catch((err) => {
      setError(err.message || "No se pudo cargar la sesión.");
    });
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadMaterials(selectedProjectId);
    }
  }, [selectedProjectId]);

  return (
    <div className="app-shell">
      <AppHeader user={user} onLogout={handleLogout} />

      <main className="dashboard-grid">
        <aside>
          <ProjectSelector
            projects={projects}
            selectedProjectId={selectedProjectId}
            onSelect={setSelectedProjectId}
          />

          {selectedProjectId && (
            <UploadForm
              projectId={selectedProjectId}
              onUploaded={() => loadMaterials(selectedProjectId)}
            />
          )}
        </aside>

        <section className="content-panel">
          <div className="content-header">
            <div>
              <p className="eyebrow">Materiales disponibles</p>
              <h2>{selectedProject?.nombre || "Sin proyecto seleccionado"}</h2>
              {selectedProject?.descripcion && <p>{selectedProject.descripcion}</p>}
            </div>

            <button className="ghost-button" onClick={() => loadMaterials()}>
              <RefreshCcw size={18} />
              Actualizar
            </button>
          </div>

          {error && <div className="error-box">{error}</div>}

          {loadingMaterials ? (
            <div className="empty-state">Cargando materiales...</div>
          ) : materials.length === 0 ? (
            <div className="empty-state">
              <ShieldCheck size={38} />
              <h3>No hay materiales visibles</h3>
              <p>Sube el primer material o selecciona otro proyecto.</p>
            </div>
          ) : (
            <div className="material-list">
              {materials.map((material) => (
                <MaterialCard
                  key={material.material_id}
                  material={material}
                  onDownload={handleDownload}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function Root() {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(localStorage.getItem("cinehub_token")));

  async function handleLogin() {
    setIsAuthenticated(true);
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return <Dashboard />;
}

createRoot(document.getElementById("root")).render(<Root />);
