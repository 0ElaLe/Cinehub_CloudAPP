from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship


metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Usuario(Base):
    __tablename__ = "Usuario"

    usuario_id = Column(Integer, primary_key=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    fecha_creacion = Column(DateTime)


class Equipo(Base):
    __tablename__ = "Equipo"

    equipo_id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(300))


class Proyecto(Base):
    __tablename__ = "Proyecto"

    proyecto_id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(500))
    estatus = Column(String(50), nullable=False)
    fecha_creacion = Column(DateTime)


class UsuarioEquipo(Base):
    __tablename__ = "UsuarioEquipo"

    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), primary_key=True)
    equipo_id = Column(Integer, ForeignKey("Equipo.equipo_id"), primary_key=True)
    rol = Column(String(100), nullable=False)
    fecha_alta = Column(DateTime)


class EquipoProyecto(Base):
    __tablename__ = "EquipoProyecto"

    equipo_id = Column(Integer, ForeignKey("Equipo.equipo_id"), primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("Proyecto.proyecto_id"), primary_key=True)
    rol_en_proyecto = Column(String(100))
    fecha_asignacion = Column(DateTime)


class Material(Base):
    __tablename__ = "Material"

    material_id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("Proyecto.proyecto_id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    tipo_material = Column(String(50), nullable=False)
    version = Column(String(30), nullable=False)
    container_name = Column(String(100), nullable=False)
    blob_path = Column(String(500), nullable=False)
    creado_por = Column(Integer, ForeignKey("Usuario.usuario_id"))
    fecha_creacion = Column(DateTime)
    nivel_confidencialidad = Column(String(50), nullable=False)


class InteraccionMaterial(Base):
    __tablename__ = "InteraccionMaterial"

    interaccion_id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("Usuario.usuario_id"), nullable=False)
    material_id = Column(Integer, ForeignKey("Material.material_id"), nullable=False)
    tipo_interaccion = Column(String(50), nullable=False)
    fecha_interaccion = Column(DateTime)
    comentario = Column(String(300))
