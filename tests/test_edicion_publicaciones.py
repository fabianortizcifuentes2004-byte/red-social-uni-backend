from tests.conftest import registrar_y_loguear


def test_autor_puede_editar_su_publicacion(client):
    headers = registrar_y_loguear(client)
    post = client.post("/api/posts", json={"contenido": "Original"}, headers=headers).get_json()
    assert post["editado"] is False

    resp = client.put(f"/api/posts/{post['id']}", json={"contenido": "Editado"}, headers=headers)
    assert resp.status_code == 200
    datos = resp.get_json()
    assert datos["contenido"] == "Editado"
    assert datos["editado"] is True


def test_editar_publicacion_de_otro_falla(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_ana).get_json()

    resp = client.put(f"/api/posts/{post['id']}", json={"contenido": "Hackeado"}, headers=headers_luis)
    assert resp.status_code == 403


def test_editar_publicacion_rechaza_contenido_vacio(client):
    headers = registrar_y_loguear(client)
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers).get_json()

    resp = client.put(f"/api/posts/{post['id']}", json={"contenido": "  "}, headers=headers)
    assert resp.status_code == 400
