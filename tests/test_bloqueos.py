from tests.conftest import registrar_y_loguear


def _id_de(client, headers):
    return client.get("/api/users/me", headers=headers).get_json()["id"]


def test_bloquear_y_ver_lo_bloqueaste(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    resp = client.post(f"/api/users/{luis_id}/bloquear", headers=headers_ana)
    assert resp.status_code == 201

    perfil = client.get(f"/api/users/{luis_id}", headers=headers_ana).get_json()
    assert perfil["lo_bloqueaste"] is True

    bloqueados = client.get("/api/users/me/bloqueados", headers=headers_ana).get_json()
    assert [u["id"] for u in bloqueados] == [luis_id]


def test_no_se_puede_bloquear_dos_veces(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    client.post(f"/api/users/{luis_id}/bloquear", headers=headers_ana)
    resp = client.post(f"/api/users/{luis_id}/bloquear", headers=headers_ana)
    assert resp.status_code == 409


def test_no_se_puede_bloquear_a_si_mismo(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    ana_id = _id_de(client, headers_ana)

    resp = client.post(f"/api/users/{ana_id}/bloquear", headers=headers_ana)
    assert resp.status_code == 400


def test_desbloquear(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    client.post(f"/api/users/{luis_id}/bloquear", headers=headers_ana)
    resp = client.delete(f"/api/users/{luis_id}/bloquear", headers=headers_ana)
    assert resp.status_code == 200

    perfil = client.get(f"/api/users/{luis_id}", headers=headers_ana).get_json()
    assert perfil["lo_bloqueaste"] is False


def test_bloqueado_no_puede_enviar_mensajes(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    ana_id = _id_de(client, headers_ana)
    luis_id = _id_de(client, headers_luis)

    client.post(f"/api/users/{luis_id}/bloquear", headers=headers_ana)

    # Ni Ana le puede escribir a Luis, ni Luis a Ana
    resp = client.post(
        "/api/messages", json={"destinatario_id": luis_id, "contenido": "Hola"}, headers=headers_ana
    )
    assert resp.status_code == 403

    resp = client.post(
        "/api/messages", json={"destinatario_id": ana_id, "contenido": "Hola"}, headers=headers_luis
    )
    assert resp.status_code == 403


def test_bloqueado_no_puede_comentar_en_tus_posts(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_ana).get_json()
    client.post(f"/api/users/{luis_id}/bloquear", headers=headers_ana)

    resp = client.post(
        f"/api/posts/{post['id']}/comentarios", json={"contenido": "Comentario"}, headers=headers_luis
    )
    assert resp.status_code == 403


def test_bloqueados_se_excluyen_de_la_busqueda(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)

    client.post(f"/api/users/{luis_id}/bloquear", headers=headers_ana)

    resultados = client.get("/api/users?q=Luis", headers=headers_ana).get_json()
    assert resultados == []

    # Y tampoco Ana aparece en la búsqueda de Luis
    resultados_luis = client.get("/api/users?q=Ana", headers=headers_luis).get_json()
    assert resultados_luis == []
