-- Ejecuta este script si aún no tienes datos de prueba.
-- Ajusta emails si en tu tabla ya existen usuarios con otros valores.

INSERT INTO Usuario (nombres, apellidos, email)
SELECT 'Ana', 'Torres', 'ana.torres@cinehub.com'
WHERE NOT EXISTS (SELECT 1 FROM Usuario WHERE email = 'ana.torres@cinehub.com');

INSERT INTO Usuario (nombres, apellidos, email)
SELECT 'Luis', 'Ramirez', 'luis.ramirez@cinehub.com'
WHERE NOT EXISTS (SELECT 1 FROM Usuario WHERE email = 'luis.ramirez@cinehub.com');

INSERT INTO Equipo (nombre, descripcion)
SELECT 'Edicion', 'Equipo encargado del montaje y cortes preliminares'
WHERE NOT EXISTS (SELECT 1 FROM Equipo WHERE nombre = 'Edicion');

INSERT INTO Equipo (nombre, descripcion)
SELECT 'Color', 'Equipo encargado de correccion de color'
WHERE NOT EXISTS (SELECT 1 FROM Equipo WHERE nombre = 'Color');

INSERT INTO Proyecto (nombre, descripcion, estatus)
SELECT 'Cortometraje Aurora', 'Proyecto cinematografico interno de prueba', 'Activo'
WHERE NOT EXISTS (SELECT 1 FROM Proyecto WHERE nombre = 'Cortometraje Aurora');

DECLARE @ana INT = (SELECT usuario_id FROM Usuario WHERE email = 'ana.torres@cinehub.com');
DECLARE @luis INT = (SELECT usuario_id FROM Usuario WHERE email = 'luis.ramirez@cinehub.com');
DECLARE @edicion INT = (SELECT equipo_id FROM Equipo WHERE nombre = 'Edicion');
DECLARE @color INT = (SELECT equipo_id FROM Equipo WHERE nombre = 'Color');
DECLARE @aurora INT = (SELECT proyecto_id FROM Proyecto WHERE nombre = 'Cortometraje Aurora');

INSERT INTO UsuarioEquipo (usuario_id, equipo_id, rol)
SELECT @ana, @edicion, 'Editora'
WHERE NOT EXISTS (SELECT 1 FROM UsuarioEquipo WHERE usuario_id = @ana AND equipo_id = @edicion);

INSERT INTO UsuarioEquipo (usuario_id, equipo_id, rol)
SELECT @luis, @color, 'Colorista'
WHERE NOT EXISTS (SELECT 1 FROM UsuarioEquipo WHERE usuario_id = @luis AND equipo_id = @color);

INSERT INTO EquipoProyecto (equipo_id, proyecto_id, rol_en_proyecto)
SELECT @edicion, @aurora, 'Edicion principal'
WHERE NOT EXISTS (SELECT 1 FROM EquipoProyecto WHERE equipo_id = @edicion AND proyecto_id = @aurora);

INSERT INTO EquipoProyecto (equipo_id, proyecto_id, rol_en_proyecto)
SELECT @color, @aurora, 'Correccion de color'
WHERE NOT EXISTS (SELECT 1 FROM EquipoProyecto WHERE equipo_id = @color AND proyecto_id = @aurora);

INSERT INTO Material (
    proyecto_id,
    nombre,
    tipo_material,
    version,
    container_name,
    blob_path,
    creado_por,
    nivel_confidencialidad
)
SELECT
    @aurora,
    'escena_01_preview_v1.mp4',
    'Video',
    'v1',
    'edited-cuts',
    'aurora/escena_01/preview_v1.mp4',
    @ana,
    'Confidencial'
WHERE NOT EXISTS (
    SELECT 1 FROM Material WHERE blob_path = 'aurora/escena_01/preview_v1.mp4'
);
