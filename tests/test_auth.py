def test_registro_exitoso(client):
    resp = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "Ana Torres",
            "correo": "ana@usanjose.edu.co",
            "password": "clave123",
        },
    )
    assert resp.status_code == 201
    assert resp.get_json()["usuario"]["correo"] == "ana@usanjose.edu.co"


def test_registro_rechaza_correo_no_institucional(client):
    resp = client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "Ana Torres",
            "correo": "ana@gmail.com",
            "password": "clave123",
        },
    )
    assert resp.status_code == 400


def test_registro_rechaza_correo_duplicado(client):
    datos = {
        "nombre_completo": "Ana Torres",
        "correo": "ana@usanjose.edu.co",
        "password": "clave123",
    }
    client.post("/api/auth/registro", json=datos)
    resp = client.post("/api/auth/registro", json=datos)
    assert resp.status_code == 409


def test_login_credenciales_invalidas(client):
    resp = client.post(
        "/api/auth/login", json={"correo": "no@usanjose.edu.co", "password": "x"}
    )
    assert resp.status_code == 401


def test_login_exitoso(client):
    client.post(
        "/api/auth/registro",
        json={
            "nombre_completo": "Ana Torres",
            "correo": "ana@usanjose.edu.co",
            "password": "clave123",
        },
    )
    resp = client.post(
        "/api/auth/login", json={"correo": "ana@usanjose.edu.co", "password": "clave123"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()
