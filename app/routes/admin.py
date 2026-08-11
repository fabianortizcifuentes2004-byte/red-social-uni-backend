from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario, RolUsuario
from app.models.publicacion import Publicacion
from app.models.comentario import Comentario
from app.models.reporte import Reporte

admin_bp = Blueprint("admin", __name__)

ROLES_VALIDOS = (RolUsuario.ESTUDIANTE, RolUsuario.DOCENTE, RolUsuario.ADMIN)


def _usuario_actual_es_admin():
    # Se re-consulta en BD (en vez de confiar en el rol grabado en el JWT) para que
    # una desactivación o cambio de rol tenga efecto inmediato, no solo al re-loguear.
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get(usuario_id)
    return usuario is not None and usuario.activo and usuario.rol == RolUsuario.ADMIN


@admin_bp.route("/usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios():
    if not _usuario_actual_es_admin():
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403

    query = Usuario.query
    activos = request.args.get("activos")
    if activos is not None:
        query = query.filter_by(activo=activos.lower() == "true")

    usuarios = query.order_by(Usuario.fecha_registro.desc()).all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@admin_bp.route("/usuarios/<int:usuario_id>", methods=["PUT"])
@jwt_required()
def actualizar_usuario(usuario_id):
    if not _usuario_actual_es_admin():
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403

    solicitante_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json() or {}

    if usuario_id == solicitante_id:
        if "activo" in data and not data["activo"]:
            return jsonify({"error": "No puedes desactivar tu propia cuenta"}), 400
        if "rol" in data and data["rol"] != RolUsuario.ADMIN:
            return jsonify({"error": "No puedes quitarte el rol de administrador a ti mismo"}), 400

    if "rol" in data:
        if data["rol"] not in ROLES_VALIDOS:
            return jsonify({"error": "Rol inválido"}), 400
        usuario.rol = data["rol"]

    if "activo" in data:
        usuario.activo = bool(data["activo"])
        if usuario.activo:
            # Si un admin reactiva manualmente una cuenta, ya no cuenta como
            # "el usuario se eliminó a sí mismo".
            usuario.eliminado_por_usuario = False

    db.session.commit()
    return jsonify(usuario.to_dict()), 200


@admin_bp.route("/estadisticas", methods=["GET"])
@jwt_required()
def estadisticas():
    if not _usuario_actual_es_admin():
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403

    hace_una_semana = datetime.now(timezone.utc) - timedelta(days=7)

    return jsonify(
        {
            "usuarios_totales": Usuario.query.count(),
            "usuarios_activos": Usuario.query.filter_by(activo=True).count(),
            "usuarios_inactivos": Usuario.query.filter_by(activo=False).count(),
            "usuarios_estudiantes": Usuario.query.filter_by(rol=RolUsuario.ESTUDIANTE).count(),
            "usuarios_docentes": Usuario.query.filter_by(rol=RolUsuario.DOCENTE).count(),
            "publicaciones_totales": Publicacion.query.count(),
            "comentarios_totales": Comentario.query.count(),
            "publicaciones_ultima_semana": Publicacion.query.filter(
                Publicacion.fecha_creacion >= hace_una_semana
            ).count(),
        }
    ), 200


@admin_bp.route("/reportes", methods=["GET"])
@jwt_required()
def listar_reportes():
    if not _usuario_actual_es_admin():
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403

    query = Reporte.query
    resuelto = request.args.get("resuelto")
    if resuelto is not None:
        query = query.filter_by(resuelto=resuelto.lower() == "true")

    reportes = query.order_by(Reporte.fecha_creacion.desc()).all()
    return jsonify([r.to_dict() for r in reportes]), 200


@admin_bp.route("/reportes/<int:reporte_id>", methods=["PUT"])
@jwt_required()
def actualizar_reporte(reporte_id):
    if not _usuario_actual_es_admin():
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403

    reporte = Reporte.query.get_or_404(reporte_id)
    data = request.get_json() or {}

    if "resuelto" in data:
        reporte.resuelto = bool(data["resuelto"])

    db.session.commit()
    return jsonify(reporte.to_dict()), 200
