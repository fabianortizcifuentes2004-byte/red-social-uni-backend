from tests.conftest import registrar_y_loguear, registrar_admin_y_loguear


def test_crear_reporte_de_publicacion(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    post = client.post("/api/posts", json={"contenido": "Contenido dudoso"}, headers=headers_luis).get_json()

    resp = client.post(
        "/api/reportes",
        json={"tipo_objetivo": "publicacion", "objetivo_id": post["id"], "motivo": "Spam"},
        headers=headers_ana,
    )
    assert resp.status_code == 201
    assert resp.get_json()["resuelto"] is False


def test_crear_reporte_rechaza_tipo_invalido(client):
    headers = registrar_y_loguear(client)
    resp = client.post(
        "/api/reportes", json={"tipo_objetivo": "usuario", "objetivo_id": 1}, headers=headers
    )
    assert resp.status_code == 400


def test_usuario_normal_no_puede_listar_reportes(client):
    headers = registrar_y_loguear(client)
    resp = client.get("/api/admin/reportes", headers=headers)
    assert resp.status_code == 403


def test_admin_lista_y_resuelve_reportes(client):
    headers_admin = registrar_admin_y_loguear(client)
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_luis).get_json()

    reporte = client.post(
        "/api/reportes",
        json={"tipo_objetivo": "publicacion", "objetivo_id": post["id"]},
        headers=headers_luis,
    ).get_json()

    lista = client.get("/api/admin/reportes", headers=headers_admin).get_json()
    assert len(lista) == 1

    resp = client.put(
        f"/api/admin/reportes/{reporte['id']}", json={"resuelto": True}, headers=headers_admin
    )
    assert resp.status_code == 200
    assert resp.get_json()["resuelto"] is True

    pendientes = client.get("/api/admin/reportes?resuelto=false", headers=headers_admin).get_json()
    assert pendientes == []
