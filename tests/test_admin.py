from tests.conftest import registrar_y_loguear, registrar_admin_y_loguear


def test_usuario_normal_no_puede_listar_usuarios(client):
    headers = registrar_y_loguear(client)
    resp = client.get("/api/admin/usuarios", headers=headers)
    assert resp.status_code == 403


def test_admin_lista_todos_los_usuarios(client):
    headers_admin = registrar_admin_y_loguear(client)
    registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    resp = client.get("/api/admin/usuarios", headers=headers_admin)
    assert resp.status_code == 200
    correos = [u["correo"] for u in resp.get_json()]
    assert "admin@usanjose.edu.co" in correos
    assert "luis@usanjose.edu.co" in correos


def test_admin_filtra_usuarios_por_activo(client):
    headers_admin = registrar_admin_y_loguear(client)
    registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    resp = client.get("/api/admin/usuarios?activos=true", headers=headers_admin)
    assert resp.status_code == 200
    assert all(u["correo"] for u in resp.get_json())


def test_admin_desactiva_usuario(client):
    headers_admin = registrar_admin_y_loguear(client)
    registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    luis = next(u for u in lista if u["correo"] == "luis@usanjose.edu.co")

    resp = client.put(f"/api/admin/usuarios/{luis['id']}", json={"activo": False}, headers=headers_admin)
    assert resp.status_code == 200

    # Un usuario desactivado no puede iniciar sesión
    resp = client.post("/api/auth/login", json={"correo": "luis@usanjose.edu.co", "password": "clave123"})
    assert resp.status_code == 403


def test_admin_cambia_rol_de_usuario(client):
    headers_admin = registrar_admin_y_loguear(client)
    registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    luis = next(u for u in lista if u["correo"] == "luis@usanjose.edu.co")

    resp = client.put(f"/api/admin/usuarios/{luis['id']}", json={"rol": "docente"}, headers=headers_admin)
    assert resp.status_code == 200
    assert resp.get_json()["rol"] == "docente"


def test_admin_rechaza_rol_invalido(client):
    headers_admin = registrar_admin_y_loguear(client)
    registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    luis = next(u for u in lista if u["correo"] == "luis@usanjose.edu.co")

    resp = client.put(f"/api/admin/usuarios/{luis['id']}", json={"rol": "superadmin"}, headers=headers_admin)
    assert resp.status_code == 400


def test_admin_no_puede_desactivarse_a_si_mismo(client):
    headers_admin = registrar_admin_y_loguear(client)
    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    admin = next(u for u in lista if u["correo"] == "admin@usanjose.edu.co")

    resp = client.put(f"/api/admin/usuarios/{admin['id']}", json={"activo": False}, headers=headers_admin)
    assert resp.status_code == 400


def test_admin_no_puede_quitarse_su_propio_rol(client):
    headers_admin = registrar_admin_y_loguear(client)
    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    admin = next(u for u in lista if u["correo"] == "admin@usanjose.edu.co")

    resp = client.put(f"/api/admin/usuarios/{admin['id']}", json={"rol": "estudiante"}, headers=headers_admin)
    assert resp.status_code == 400


def test_cuenta_desactivada_pierde_acceso_admin_de_inmediato(client):
    """El chequeo de admin re-consulta la BD, no confía solo en el claim del JWT."""
    headers_admin = registrar_admin_y_loguear(client)
    otro_admin_headers = registrar_admin_y_loguear(client, correo="otro-admin@usanjose.edu.co", nombre="Otro Admin")

    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    primero = next(u for u in lista if u["correo"] == "admin@usanjose.edu.co")

    # El segundo admin desactiva al primero sin que este vuelva a loguearse
    client.put(f"/api/admin/usuarios/{primero['id']}", json={"activo": False}, headers=otro_admin_headers)

    resp = client.get("/api/admin/usuarios", headers=headers_admin)
    assert resp.status_code == 403


def test_admin_obtiene_estadisticas(client):
    headers_admin = registrar_admin_y_loguear(client)
    client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_admin)

    resp = client.get("/api/admin/estadisticas", headers=headers_admin)
    assert resp.status_code == 200
    datos = resp.get_json()
    assert datos["usuarios_totales"] == 1
    assert datos["publicaciones_totales"] == 1


def test_admin_puede_borrar_publicacion_de_otro(client):
    headers_admin = registrar_admin_y_loguear(client)
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_luis).get_json()

    resp = client.delete(f"/api/posts/{post['id']}", headers=headers_admin)
    assert resp.status_code == 200


def test_admin_puede_borrar_comentario_de_otro(client):
    headers_admin = registrar_admin_y_loguear(client)
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_luis).get_json()
    comentario = client.post(
        f"/api/posts/{post['id']}/comentarios", json={"contenido": "Comentario"}, headers=headers_luis
    ).get_json()

    resp = client.delete(
        f"/api/posts/{post['id']}/comentarios/{comentario['id']}", headers=headers_admin
    )
    assert resp.status_code == 200
