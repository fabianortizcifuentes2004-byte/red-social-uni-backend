import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required
import cloudinary
import cloudinary.uploader

uploads_bp = Blueprint("uploads", __name__)

EXTENSIONES_PERMITIDAS = {"jpg", "jpeg", "png", "webp"}


def _extension(nombre_archivo):
    if "." not in nombre_archivo:
        return None
    return nombre_archivo.rsplit(".", 1)[1].lower()


@uploads_bp.route("", methods=["POST"])
@jwt_required()
def subir_imagen():
    archivo = request.files.get("archivo")
    if not archivo or archivo.filename == "":
        return jsonify({"error": "Debes adjuntar un archivo con el campo 'archivo'"}), 400

    extension = _extension(archivo.filename)
    if extension not in EXTENSIONES_PERMITIDAS:
        return jsonify({"error": "Formato no permitido (usa jpg, jpeg, png o webp)"}), 400

    cloudinary_url = current_app.config.get("CLOUDINARY_URL")
    if cloudinary_url:
        # Hosts sin disco persistente (p.ej. el plan gratuito de Render) no
        # pueden guardar archivos localmente entre despliegues/reinicios.
        cloudinary.config(cloudinary_url=cloudinary_url)
        resultado = cloudinary.uploader.upload(archivo, resource_type="image")
        return jsonify({"url": resultado["secure_url"]}), 201

    carpeta = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(carpeta, exist_ok=True)

    nombre_unico = f"{uuid.uuid4().hex}.{extension}"
    archivo.save(os.path.join(carpeta, nombre_unico))

    return jsonify({"url": f"/api/uploads/{nombre_unico}"}), 201


@uploads_bp.route("/<path:nombre_archivo>", methods=["GET"])
def obtener_imagen(nombre_archivo):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], nombre_archivo)
