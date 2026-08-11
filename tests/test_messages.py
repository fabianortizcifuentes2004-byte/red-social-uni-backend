from tests.conftest import registrar_y_loguear


def test_enviar_y_ver_conversacion(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    luis_id = client.get("/api/users/me", headers=headers_luis).get_json()["id"]

    resp = client.post(
        "/api/messages",
        json={"destinatario_id": luis_id, "contenido": "Hola Luis"},
        headers=headers_ana,
    )
    assert resp.status_code == 201

    resp = client.get(f"/api/messages/conversacion/{luis_id}", headers=headers_ana)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_conversacion_marca_como_leido(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")

    ana_id = client.get("/api/users/me", headers=headers_ana).get_json()["id"]
    luis_id = client.get("/api/users/me", headers=headers_luis).get_json()["id"]

    client.post(
        "/api/messages",
        json={"destinatario_id": luis_id, "contenido": "Hola Luis"},
        headers=headers_ana,
    )

    # Antes de que Luis abra el hilo, el mensaje debe figurar como no leído
    conversaciones = client.get("/api/messages/conversaciones", headers=headers_luis).get_json()
    assert conversaciones[0]["no_leidos"] == 1

    client.get(f"/api/messages/conversacion/{ana_id}", headers=headers_luis)

    conversaciones = client.get("/api/messages/conversaciones", headers=headers_luis).get_json()
    assert conversaciones[0]["no_leidos"] == 0


def test_listar_conversaciones_ordena_por_mas_reciente(client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    headers_ivan = registrar_y_loguear(client, correo="ivan@usanjose.edu.co", nombre="Ivan")

    luis_id = client.get("/api/users/me", headers=headers_luis).get_json()["id"]
    ivan_id = client.get("/api/users/me", headers=headers_ivan).get_json()["id"]

    client.post(
        "/api/messages",
        json={"destinatario_id": luis_id, "contenido": "Primero"},
        headers=headers_ana,
    )
    client.post(
        "/api/messages",
        json={"destinatario_id": ivan_id, "contenido": "Segundo"},
        headers=headers_ana,
    )

    conversaciones = client.get("/api/messages/conversaciones", headers=headers_ana).get_json()
    assert len(conversaciones) == 2
    assert conversaciones[0]["usuario"]["nombre_completo"] == "Ivan"
    assert conversaciones[1]["usuario"]["nombre_completo"] == "Luis"
