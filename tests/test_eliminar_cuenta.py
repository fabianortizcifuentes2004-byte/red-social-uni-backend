from tests.conftest import registrar_y_loguear, registrar_admin_y_loguear


def test_eliminar_cuenta_requiere_password_correcto(client):
    headers = registrar_y_loguear(client)
    resp = client.delete("/api/users/me", json={"password": "incorrecta"}, headers=headers)
    assert resp.status_code == 401


def test_eliminar_cuenta_propia(client):
    headers = registrar_y_loguear(client)
    resp = client.delete("/api/users/me", json={"password": "clave123"}, headers=headers)
    assert resp.status_code == 200

    # Ya no puede iniciar sesión
    resp = client.post("/api/auth/login", json={"correo": "ana@usanjose.edu.co", "password": "clave123"})
    assert resp.status_code == 403


def test_admin_distingue_cuenta_autoeliminada_de_baneada(client):
    headers_admin = registrar_admin_y_loguear(client)
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    headers_maria = registrar_y_loguear(client, correo="maria@usanjose.edu.co", nombre="Maria")

    # Luis se elimina a sí mismo
    client.delete("/api/users/me", json={"password": "clave123"}, headers=headers_luis)

    # Un admin banea a Maria
    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    maria = next(u for u in lista if u["correo"] == "maria@usanjose.edu.co")
    client.put(f"/api/admin/usuarios/{maria['id']}", json={"activo": False}, headers=headers_admin)

    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    luis = next(u for u in lista if u["correo"] == "luis@usanjose.edu.co")
    maria = next(u for u in lista if u["correo"] == "maria@usanjose.edu.co")

    assert luis["activo"] is False
    assert maria["activo"] is False


def test_admin_reactivar_limpia_eliminado_por_usuario(client):
    from app.models.usuario import Usuario

    headers_admin = registrar_admin_y_loguear(client)
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    client.delete("/api/users/me", json={"password": "clave123"}, headers=headers_luis)

    lista = client.get("/api/admin/usuarios", headers=headers_admin).get_json()
    luis = next(u for u in lista if u["correo"] == "luis@usanjose.edu.co")

    client.put(f"/api/admin/usuarios/{luis['id']}", json={"activo": True}, headers=headers_admin)

    usuario = Usuario.query.get(luis["id"])
    assert usuario.activo is True
    assert usuario.eliminado_por_usuario is False
