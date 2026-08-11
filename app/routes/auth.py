from datetime import timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from app import db, limiter
from app.models.usuario import Usuario, RolUsuario

auth_bp = Blueprint("auth", __name__)

NOMBRE_MAX = 150


@auth_bp.route("/registro", methods=["POST"])
@limiter.limit("10 per minute")
def registro():
    data = request.get_json() or {}

    nombre_completo = data.get("nombre_completo", "").strip()
    correo = data.get("correo", "").strip().lower()
    password = data.get("password", "")
    rol = data.get("rol", RolUsuario.ESTUDIANTE)
    facultad = data.get("facultad")
    carrera = data.get("carrera")

    if not nombre_completo or not correo or not password:
        return jsonify({"error": "nombre_completo, correo y password son obligatorios"}), 400

    if len(nombre_completo) > NOMBRE_MAX:
        return jsonify({"error": f"El nombre no puede superar los {NOMBRE_MAX} caracteres"}), 400

    dominio = current_app.config["DOMINIO_INSTITUCIONAL"]
    if not correo.endswith(f"@{dominio}"):
        return jsonify({"error": f"Debes registrarte con tu correo institucional (@{dominio})"}), 400

    if rol not in (RolUsuario.ESTUDIANTE, RolUsuario.DOCENTE):
        return jsonify({"error": "rol inválido"}), 400

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "Ya existe una cuenta con ese correo"}), 409

    usuario = Usuario(
        nombre_completo=nombre_completo,
        correo=correo,
        rol=rol,
        facultad=facultad,
        carrera=carrera,
    )
    usuario.set_password(password)

    db.session.add(usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario registrado con éxito", "usuario": usuario.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json() or {}
    correo = data.get("correo", "").strip().lower()
    password = data.get("password", "")

    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario or not usuario.check_password(password):
        return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    if not usuario.activo:
        return jsonify({"error": "Cuenta inactiva, contacta al administrador"}), 403

    token = create_access_token(
        identity=str(usuario.id),
        expires_delta=timedelta(hours=current_app.config["JWT_ACCESS_TOKEN_EXPIRES_HORAS"]),
        additional_claims={"rol": usuario.rol},
    )

    return jsonify({"access_token": token, "usuario": usuario.to_dict()}), 200
