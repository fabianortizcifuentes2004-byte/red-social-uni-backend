from tests.conftest import registrar_y_loguear


def _id_de(client, headers):
    return client.get("/api/users/me", headers=headers).get_json()["id"]


def test_seguir_y_ver_contadores(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    resp = client.post(f"/api/users/{luis_id}/seguir", headers=headers_ana)
    assert resp.status_code == 201

    perfil_luis = client.get(f"/api/users/{luis_id}", headers=headers_ana).get_json()
    assert perfil_luis["total_seguidores"] == 1
    assert perfil_luis["lo_sigues"] is True

    perfil_luis_desde_si_mismo = client.get(f"/api/users/{luis_id}", headers=headers_luis).get_json()
    assert perfil_luis_desde_si_mismo["lo_sigues"] is False  # no aplica sobre uno mismo


def test_no_se_puede_seguir_dos_veces(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    client.post(f"/api/users/{luis_id}/seguir", headers=headers_ana)
    resp = client.post(f"/api/users/{luis_id}/seguir", headers=headers_ana)
    assert resp.status_code == 409


def test_no_se_puede_seguir_a_si_mismo(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    ana_id = _id_de(client, headers_ana)

    resp = client.post(f"/api/users/{ana_id}/seguir", headers=headers_ana)
    assert resp.status_code == 400


def test_dejar_de_seguir(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    client.post(f"/api/users/{luis_id}/seguir", headers=headers_ana)
    resp = client.delete(f"/api/users/{luis_id}/seguir", headers=headers_ana)
    assert resp.status_code == 200

    perfil_luis = client.get(f"/api/users/{luis_id}", headers=headers_ana).get_json()
    assert perfil_luis["total_seguidores"] == 0
    assert perfil_luis["lo_sigues"] is False


def test_listar_seguidores_y_siguiendo(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    ana_id = _id_de(client, headers_ana)
    luis_id = _id_de(client, headers_luis)

    client.post(f"/api/users/{luis_id}/seguir", headers=headers_ana)

    seguidores_de_luis = client.get(f"/api/users/{luis_id}/seguidores", headers=headers_ana).get_json()
    assert [u["id"] for u in seguidores_de_luis] == [ana_id]

    siguiendo_de_ana = client.get(f"/api/users/{ana_id}/siguiendo", headers=headers_ana).get_json()
    assert [u["id"] for u in siguiendo_de_ana] == [luis_id]


def test_busqueda_filtra_por_facultad_y_carrera(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana Torres")
    client.put(
        "/api/users/me", json={"facultad": "Ingeniería", "carrera": "Sistemas"}, headers=headers_ana
    )

    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    client.put(
        "/api/users/me",
        json={"facultad": "Ciencias Sociales", "carrera": "Psicología"},
        headers=headers_luis,
    )

    resp = client.get("/api/users?facultad=Ingenier%C3%ADa", headers=headers_ana)
    assert resp.status_code == 200
    nombres = [u["nombre_completo"] for u in resp.get_json()]
    assert "Ana Torres" in nombres
    assert "Luis" not in nombres

    resp = client.get("/api/users?carrera=Psicolog%C3%ADa", headers=headers_ana)
    nombres = [u["nombre_completo"] for u in resp.get_json()]
    assert "Luis" in nombres
