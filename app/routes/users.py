from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario
from app.models.seguidor import Seguidor
from app.models.bloqueo import Bloqueo
from app.utils.notificaciones import enviar_notificacion

users_bp = Blueprint("users", __name__)

LONGITUDES_MAXIMAS = {
    "nombre_completo": 150,
    "facultad": 100,
    "carrera": 100,
    "foto_url": 255,
    "biografia": 280,
}


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def mi_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify(usuario.to_dict()), 200


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def editar_perfil():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json() or {}

    for campo, maximo in LONGITUDES_MAXIMAS.items():
        if campo in data and data[campo] and len(data[campo]) > maximo:
            return jsonify({"error": f"{campo} no puede superar los {maximo} caracteres"}), 400

    for campo in LONGITUDES_MAXIMAS:
        if campo in data:
            setattr(usuario, campo, data[campo])

    db.session.commit()
    return jsonify(usuario.to_dict()), 200


@users_bp.route("/me/push-token", methods=["PUT"])
@jwt_required()
def actualizar_push_token():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json() or {}

    usuario.push_token = data.get("push_token") or None
    db.session.commit()
    return jsonify({"mensaje": "Token actualizado"}), 200


@users_bp.route("/me", methods=["DELETE"])
@jwt_required()
def eliminar_mi_cuenta():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json() or {}

    if not usuario.check_password(data.get("password", "")):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    usuario.activo = False
    usuario.eliminado_por_usuario = True
    db.session.commit()
    return jsonify({"mensaje": "Cuenta eliminada"}), 200


@users_bp.route("/me/bloqueados", methods=["GET"])
@jwt_required()
def listar_bloqueados():
    usuario_id = int(get_jwt_identity())
    bloqueados = (
        Usuario.query.join(Bloqueo, Bloqueo.bloqueado_id == Usuario.id)
        .filter(Bloqueo.bloqueador_id == usuario_id)
        .all()
    )
    return jsonify([u.to_dict() for u in bloqueados]), 200


@users_bp.route("/<int:usuario_id>", methods=["GET"])
@jwt_required()
def ver_perfil(usuario_id):
    solicitante_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)

    datos = usuario.to_dict()
    datos["total_seguidores"] = Seguidor.query.filter_by(seguido_id=usuario_id).count()
    datos["total_siguiendo"] = Seguidor.query.filter_by(seguidor_id=usuario_id).count()
    datos["lo_sigues"] = (
        usuario_id != solicitante_id
        and Seguidor.query.filter_by(seguidor_id=solicitante_id, seguido_id=usuario_id).first()
        is not None
    )
    datos["lo_bloqueaste"] = (
        usuario_id != solicitante_id
        and Bloqueo.query.filter_by(bloqueador_id=solicitante_id, bloqueado_id=usuario_id).first()
        is not None
    )
    return jsonify(datos), 200


@users_bp.route("", methods=["GET"])
@jwt_required()
def buscar_usuarios():
    """Búsqueda por nombre y/o filtros: /api/users?q=juan&facultad=...&carrera=..."""
    q = request.args.get("q", "").strip()
    facultad = request.args.get("facultad", "").strip()
    carrera = request.args.get("carrera", "").strip()

    solicitante_id = int(get_jwt_identity())

    query = Usuario.query.filter_by(activo=True)
    if q:
        query = query.filter(Usuario.nombre_completo.ilike(f"%{q}%"))
    if facultad:
        query = query.filter(Usuario.facultad.ilike(f"%{facultad}%"))
    if carrera:
        query = query.filter(Usuario.carrera.ilike(f"%{carrera}%"))

    ids_bloqueados = {
        b.bloqueado_id for b in Bloqueo.query.filter_by(bloqueador_id=solicitante_id).all()
    } | {
        b.bloqueador_id for b in Bloqueo.query.filter_by(bloqueado_id=solicitante_id).all()
    }
    if ids_bloqueados:
        query = query.filter(~Usuario.id.in_(ids_bloqueados))

    usuarios = query.limit(30).all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@users_bp.route("/<int:usuario_id>/bloquear", methods=["POST"])
@jwt_required()
def bloquear_usuario(usuario_id):
    bloqueador_id = int(get_jwt_identity())
    Usuario.query.get_or_404(usuario_id)

    if bloqueador_id == usuario_id:
        return jsonify({"error": "No puedes bloquearte a ti mismo"}), 400

    existente = Bloqueo.query.filter_by(bloqueador_id=bloqueador_id, bloqueado_id=usuario_id).first()
    if existente:
        return jsonify({"error": "Ya bloqueaste a este usuario"}), 409

    bloqueo = Bloqueo(bloqueador_id=bloqueador_id, bloqueado_id=usuario_id)
    db.session.add(bloqueo)
    db.session.commit()
    return jsonify({"mensaje": "Usuario bloqueado"}), 201


@users_bp.route("/<int:usuario_id>/bloquear", methods=["DELETE"])
@jwt_required()
def desbloquear_usuario(usuario_id):
    bloqueador_id = int(get_jwt_identity())

    existente = Bloqueo.query.filter_by(bloqueador_id=bloqueador_id, bloqueado_id=usuario_id).first()
    if existente:
        db.session.delete(existente)
        db.session.commit()

    return jsonify({"mensaje": "Usuario desbloqueado"}), 200


@users_bp.route("/<int:usuario_id>/seguir", methods=["POST"])
@jwt_required()
def seguir_usuario(usuario_id):
    seguidor_id = int(get_jwt_identity())
    Usuario.query.get_or_404(usuario_id)

    if seguidor_id == usuario_id:
        return jsonify({"error": "No puedes seguirte a ti mismo"}), 400

    existente = Seguidor.query.filter_by(seguidor_id=seguidor_id, seguido_id=usuario_id).first()
    if existente:
        return jsonify({"error": "Ya sigues a este usuario"}), 409

    seguimiento = Seguidor(seguidor_id=seguidor_id, seguido_id=usuario_id)
    db.session.add(seguimiento)
    db.session.commit()

    seguidor = Usuario.query.get(seguidor_id)
    enviar_notificacion(
        usuario_id,
        "Nuevo seguidor",
        f"{seguidor.nombre_completo} empezó a seguirte",
        datos={"tipo": "seguidor", "usuario_id": seguidor_id},
    )

    return jsonify({"mensaje": "Ahora sigues a este usuario"}), 201


@users_bp.route("/<int:usuario_id>/seguir", methods=["DELETE"])
@jwt_required()
def dejar_de_seguir(usuario_id):
    seguidor_id = int(get_jwt_identity())

    existente = Seguidor.query.filter_by(seguidor_id=seguidor_id, seguido_id=usuario_id).first()
    if existente:
        db.session.delete(existente)
        db.session.commit()

    return jsonify({"mensaje": "Dejaste de seguir a este usuario"}), 200


@users_bp.route("/<int:usuario_id>/seguidores", methods=["GET"])
@jwt_required()
def listar_seguidores(usuario_id):
    Usuario.query.get_or_404(usuario_id)
    seguidores = (
        Usuario.query.join(Seguidor, Seguidor.seguidor_id == Usuario.id)
        .filter(Seguidor.seguido_id == usuario_id)
        .all()
    )
    return jsonify([u.to_dict() for u in seguidores]), 200


@users_bp.route("/<int:usuario_id>/siguiendo", methods=["GET"])
@jwt_required()
def listar_siguiendo(usuario_id):
    Usuario.query.get_or_404(usuario_id)
    siguiendo = (
        Usuario.query.join(Seguidor, Seguidor.seguido_id == Usuario.id)
        .filter(Seguidor.seguidor_id == usuario_id)
        .all()
    )
    return jsonify([u.to_dict() for u in siguiendo]), 200
