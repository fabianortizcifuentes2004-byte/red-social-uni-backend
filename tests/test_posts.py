from tests.conftest import registrar_y_loguear


def test_crear_y_listar_publicacion(client):
    headers = registrar_y_loguear(client)

    resp = client.post("/api/posts", json={"contenido": "Hola mundo"}, headers=headers)
    assert resp.status_code == 201

    resp = client.get("/api/posts", headers=headers)
    assert resp.status_code == 200
    publicaciones = resp.get_json()
    assert len(publicaciones) == 1
    assert publicaciones[0]["contenido"] == "Hola mundo"


def test_crear_publicacion_vacia_falla(client):
    headers = registrar_y_loguear(client)
    resp = client.post("/api/posts", json={"contenido": "  "}, headers=headers)
    assert resp.status_code == 400


def test_like_toggle(client):
    headers = registrar_y_loguear(client)
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers).get_json()

    resp = client.post(f"/api/posts/{post['id']}/like", headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()["like"] is True

    resp = client.post(f"/api/posts/{post['id']}/like", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["like"] is False


def test_comentar_publicacion(client):
    headers = registrar_y_loguear(client)
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers).get_json()

    resp = client.post(
        f"/api/posts/{post['id']}/comentarios", json={"contenido": "Buen post"}, headers=headers
    )
    assert resp.status_code == 201

    resp = client.get(f"/api/posts/{post['id']}/comentarios", headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_eliminar_publicacion_de_otro_usuario_falla(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_ana).get_json()

    resp = client.delete(f"/api/posts/{post['id']}", headers=headers_luis)
    assert resp.status_code == 403


def test_autor_puede_eliminar_su_propio_comentario(client):
    headers = registrar_y_loguear(client)
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers).get_json()
    comentario = client.post(
        f"/api/posts/{post['id']}/comentarios", json={"contenido": "Mi comentario"}, headers=headers
    ).get_json()

    resp = client.delete(f"/api/posts/{post['id']}/comentarios/{comentario['id']}", headers=headers)
    assert resp.status_code == 200

    comentarios = client.get(f"/api/posts/{post['id']}/comentarios", headers=headers).get_json()
    assert comentarios == []


def test_eliminar_comentario_de_otro_usuario_falla(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_ana).get_json()
    comentario = client.post(
        f"/api/posts/{post['id']}/comentarios", json={"contenido": "Comentario de Ana"}, headers=headers_ana
    ).get_json()

    resp = client.delete(
        f"/api/posts/{post['id']}/comentarios/{comentario['id']}", headers=headers_luis
    )
    assert resp.status_code == 403


def test_comentario_incluye_usuario_id(client):
    headers = registrar_y_loguear(client)
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers).get_json()
    comentario = client.post(
        f"/api/posts/{post['id']}/comentarios", json={"contenido": "Hola"}, headers=headers
    ).get_json()
    assert "usuario_id" in comentario
