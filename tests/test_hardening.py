from tests.conftest import registrar_y_loguear


def test_registro_rechaza_nombre_muy_largo(client):
    resp = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "A" * 151,
            "correo": "ana@usanjose.edu.co",
            "password": "clave123",
        },
    )
    assert resp.status_code == 400


def test_crear_publicacion_rechaza_contenido_muy_largo(client):
    headers = registrar_y_loguear(client)
    resp = client.post("/api/posts", json={"contenido": "x" * 5001}, headers=headers)
    assert resp.status_code == 400


def test_comentar_rechaza_contenido_muy_largo(client):
    headers = registrar_y_loguear(client)
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers).get_json()
    resp = client.post(
        f"/api/posts/{post['id']}/comentarios", json={"contenido": "x" * 501}, headers=headers
    )
    assert resp.status_code == 400


def test_enviar_mensaje_rechaza_contenido_muy_largo(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = client.get("/api/users/me", headers=headers_luis).get_json()["id"]

    resp = client.post(
        "/api/messages",
        json={"destinatario_id": luis_id, "contenido": "x" * 2001},
        headers=headers_ana,
    )
    assert resp.status_code == 400


def test_editar_perfil_rechaza_biografia_muy_larga(client):
    headers = registrar_y_loguear(client)
    resp = client.put("/api/users/me", json={"biografia": "x" * 281}, headers=headers)
    assert resp.status_code == 400


def test_cors_configurable_por_env(client, app):
    with app.app_context():
        assert app.config["ORIGENES_PERMITIDOS"] == "*"


def test_env_sobreescribe_los_secretos_de_ejemplo_inseguros():
    """El backend trae un .env local (gitignored) con secretos generados
    aleatoriamente; confirma que config.Config ya no usa los valores de
    ejemplo hardcodeados como fallback."""
    import importlib
    import config

    importlib.reload(config)
    assert config.Config.SECRET_KEY != "cambia-esta-clave-en-produccion"
    assert config.Config.JWT_SECRET_KEY != "cambia-esta-clave-jwt"
