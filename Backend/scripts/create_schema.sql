-- =============================================================================
-- CineHub Materials — Esquema de base de datos
-- Base de datos: sqldb-cinehub-lab-metadata-01
-- SQL Server:    sql-cinehub-lab-data-01.database.windows.net
--
-- Ejecuta este script UNA VEZ antes del primer despliegue.
-- Es idempotente: no falla si las tablas ya existen.
-- =============================================================================

-- Tabla de usuarios de la plataforma
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Usuario'
)
CREATE TABLE Usuario (
    usuario_id     INT IDENTITY(1,1) NOT NULL,
    nombres        NVARCHAR(100)     NOT NULL,
    apellidos      NVARCHAR(100)     NOT NULL,
    email          NVARCHAR(150)     NOT NULL,
    fecha_creacion DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT PK_Usuario  PRIMARY KEY (usuario_id),
    CONSTRAINT UQ_Usuario_email UNIQUE (email)
);

-- Equipos de trabajo (Edición, Color, Audio, etc.)
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Equipo'
)
CREATE TABLE Equipo (
    equipo_id   INT IDENTITY(1,1) NOT NULL,
    nombre      NVARCHAR(100)     NOT NULL,
    descripcion NVARCHAR(300)     NULL,
    CONSTRAINT PK_Equipo PRIMARY KEY (equipo_id)
);

-- Proyectos cinematográficos
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Proyecto'
)
CREATE TABLE Proyecto (
    proyecto_id   INT IDENTITY(1,1) NOT NULL,
    nombre        NVARCHAR(150)     NOT NULL,
    descripcion   NVARCHAR(500)     NULL,
    estatus       NVARCHAR(50)      NOT NULL DEFAULT 'Activo',
    fecha_creacion DATETIME2        NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT PK_Proyecto PRIMARY KEY (proyecto_id)
);

-- Relación Usuario ↔ Equipo (un usuario puede pertenecer a varios equipos)
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'UsuarioEquipo'
)
CREATE TABLE UsuarioEquipo (
    usuario_id INT           NOT NULL,
    equipo_id  INT           NOT NULL,
    rol        NVARCHAR(100) NOT NULL,
    fecha_alta DATETIME2     NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT PK_UsuarioEquipo PRIMARY KEY (usuario_id, equipo_id),
    CONSTRAINT FK_UE_Usuario FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id),
    CONSTRAINT FK_UE_Equipo  FOREIGN KEY (equipo_id)  REFERENCES Equipo(equipo_id)
);

-- Relación Equipo ↔ Proyecto (un equipo puede trabajar en varios proyectos)
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'EquipoProyecto'
)
CREATE TABLE EquipoProyecto (
    equipo_id        INT           NOT NULL,
    proyecto_id      INT           NOT NULL,
    rol_en_proyecto  NVARCHAR(100) NULL,
    fecha_asignacion DATETIME2     NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT PK_EquipoProyecto PRIMARY KEY (equipo_id, proyecto_id),
    CONSTRAINT FK_EP_Equipo   FOREIGN KEY (equipo_id)   REFERENCES Equipo(equipo_id),
    CONSTRAINT FK_EP_Proyecto FOREIGN KEY (proyecto_id) REFERENCES Proyecto(proyecto_id)
);

-- Materiales: metadatos de cada archivo almacenado en Azure Blob Storage
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Material'
)
CREATE TABLE Material (
    material_id            INT IDENTITY(1,1) NOT NULL,
    proyecto_id            INT               NOT NULL,
    nombre                 NVARCHAR(200)     NOT NULL,
    tipo_material          NVARCHAR(50)      NOT NULL,       -- Video, Audio, Imagen, Script, etc.
    version                NVARCHAR(30)      NOT NULL DEFAULT 'v1',
    container_name         NVARCHAR(100)     NOT NULL,       -- Contenedor en Blob Storage
    blob_path              NVARCHAR(500)     NOT NULL,       -- Ruta dentro del contenedor
    creado_por             INT               NULL,
    fecha_creacion         DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
    nivel_confidencialidad NVARCHAR(50)      NOT NULL DEFAULT 'Interno', -- Interno / Confidencial / Restringido
    CONSTRAINT PK_Material  PRIMARY KEY (material_id),
    CONSTRAINT FK_M_Proyecto FOREIGN KEY (proyecto_id) REFERENCES Proyecto(proyecto_id),
    CONSTRAINT FK_M_Usuario  FOREIGN KEY (creado_por)  REFERENCES Usuario(usuario_id)
);

-- Auditoría de interacciones (SUBIDA, DESCARGA) por usuario y material
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'InteraccionMaterial'
)
CREATE TABLE InteraccionMaterial (
    interaccion_id    INT IDENTITY(1,1) NOT NULL,
    usuario_id        INT               NOT NULL,
    material_id       INT               NOT NULL,
    tipo_interaccion  NVARCHAR(50)      NOT NULL,  -- SUBIDA | DESCARGA
    fecha_interaccion DATETIME2         NOT NULL DEFAULT GETUTCDATE(),
    comentario        NVARCHAR(300)     NULL,
    CONSTRAINT PK_InteraccionMaterial PRIMARY KEY (interaccion_id),
    CONSTRAINT FK_IM_Usuario  FOREIGN KEY (usuario_id)  REFERENCES Usuario(usuario_id),
    CONSTRAINT FK_IM_Material FOREIGN KEY (material_id) REFERENCES Material(material_id)
);

-- Índices para consultas frecuentes
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Material_proyecto_id')
    CREATE INDEX IX_Material_proyecto_id ON Material(proyecto_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_InteraccionMaterial_material_id')
    CREATE INDEX IX_InteraccionMaterial_material_id ON InteraccionMaterial(material_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_UsuarioEquipo_equipo_id')
    CREATE INDEX IX_UsuarioEquipo_equipo_id ON UsuarioEquipo(equipo_id);

PRINT 'Esquema CineHub creado/verificado correctamente.';
