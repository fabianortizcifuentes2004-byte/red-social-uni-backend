import io

from tests.conftest import registrar_y_loguear


def _archivo_png():
    # PNG 1x1 válido mínimo
    contenido = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
        "de0000000c4944415478da6360606060000000050001a5f645400000000049454e44ae426082"
    )
    return io.BytesIO(contenido)


def test_subir_imagen_valida(client):
    headers = registrar_y_loguear(client)

    resp = client.post(
        "/api/uploads",
        data={"archivo": (_archivo_png(), "foto.png")},
        content_type="multipart/form-data",
        headers=headers,
    )
    assert resp.status_code == 201
    url = resp.get_json()["url"]
    assert url.startswith("/api/uploads/")
    assert url.endswith(".png")

    # El archivo debe quedar accesible vía GET (sin autenticación)
    nombre_archivo = url.rsplit("/", 1)[1]
    resp = client.get(f"/api/uploads/{nombre_archivo}")
    assert resp.status_code == 200


def test_subir_imagen_requiere_autenticacion(client):
    resp = client.post(
        "/api/uploads",
        data={"archivo": (_archivo_png(), "foto.png")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 401


def test_subir_imagen_rechaza_extension_no_permitida(client):
    headers = registrar_y_loguear(client)

    resp = client.post(
        "/api/uploads",
        data={"archivo": (io.BytesIO(b"contenido"), "archivo.exe")},
        content_type="multipart/form-data",
        headers=headers,
    )
    assert resp.status_code == 400


def test_subir_sin_archivo_falla(client):
    headers = registrar_y_loguear(client)

    resp = client.post("/api/uploads", data={}, content_type="multipart/form-data", headers=headers)
    assert resp.status_code == 400
