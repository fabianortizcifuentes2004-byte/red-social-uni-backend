from unittest.mock import patch

from tests.conftest import registrar_y_loguear


def _id_de(client, headers):
    return client.get("/api/users/me", headers=headers).get_json()["id"]


def _asignar_push_token(client, headers, token="ExponentPushToken[falso]"):
    resp = client.put("/api/users/me/push-token", json={"push_token": token}, headers=headers)
    assert resp.status_code == 200


@patch("app.utils.notificaciones.requests.post")
def test_mensaje_dispara_notificacion(mock_post, client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)
    _asignar_push_token(client, headers_luis)

    resp = client.post(
        "/api/messages", json={"destinatario_id": luis_id, "contenido": "Hola"}, headers=headers_ana
    )
    assert resp.status_code == 201
    mock_post.assert_called_once()
    payload = mock_post.call_args.kwargs["json"]
    assert payload["to"] == "ExponentPushToken[falso]"
    assert payload["data"]["tipo"] == "mensaje"


@patch("app.utils.notificaciones.requests.post")
def test_sin_push_token_no_llama_a_expo(mock_post, client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)
    # Luis nunca registró push_token

    resp = client.post(
        "/api/messages", json={"destinatario_id": luis_id, "contenido": "Hola"}, headers=headers_ana
    )
    assert resp.status_code == 201
    mock_post.assert_not_called()


@patch("app.utils.notificaciones.requests.post", side_effect=Exception("red caída"))
def test_fallo_de_red_no_rompe_la_request(mock_post, client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)
    _asignar_push_token(client, headers_luis)

    resp = client.post(
        "/api/messages", json={"destinatario_id": luis_id, "contenido": "Hola"}, headers=headers_ana
    )
    assert resp.status_code == 201  # el mensaje se envía igual aunque el push falle


@patch("app.utils.notificaciones.requests.post")
def test_comentario_dispara_notificacion_al_autor_no_a_si_mismo(mock_post, client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    _asignar_push_token(client, headers_ana)

    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_ana).get_json()

    # Ana comenta su propio post: no debería notificarse a sí misma
    client.post(f"/api/posts/{post['id']}/comentarios", json={"contenido": "Yo"}, headers=headers_ana)
    mock_post.assert_not_called()

    # Luis comenta el post de Ana: sí debería notificarse
    client.post(f"/api/posts/{post['id']}/comentarios", json={"contenido": "Hola Ana"}, headers=headers_luis)
    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["json"]["data"]["tipo"] == "comentario"


@patch("app.utils.notificaciones.requests.post")
def test_like_dispara_notificacion_solo_al_agregar(mock_post, client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    _asignar_push_token(client, headers_ana)

    post = client.post("/api/posts", json={"contenido": "Hola"}, headers=headers_ana).get_json()

    client.post(f"/api/posts/{post['id']}/like", headers=headers_luis)
    mock_post.assert_called_once()

    mock_post.reset_mock()
    client.post(f"/api/posts/{post['id']}/like", headers=headers_luis)  # retira el like
    mock_post.assert_not_called()


@patch("app.utils.notificaciones.requests.post")
def test_seguir_dispara_notificacion(mock_post, client):
    headers_ana = registrar_y_loguear(client, correo="ana@usanjose.edu.co", nombre="Ana")
    headers_luis = registrar_y_loguear(client, correo="luis@usanjose.edu.co", nombre="Luis")
    luis_id = _id_de(client, headers_luis)
    _asignar_push_token(client, headers_luis)

    client.post(f"/api/users/{luis_id}/seguir", headers=headers_ana)
    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["json"]["data"]["tipo"] == "seguidor"
