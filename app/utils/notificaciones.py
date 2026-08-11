import requests

from app.models.usuario import Usuario

URL_PUSH_EXPO = "https://exp.host/--/api/v2/push/send"


def enviar_notificacion(usuario_id, titulo, cuerpo, datos=None):
    """Envía una notificación push al usuario si tiene un token registrado.

    Nunca lanza una excepción hacia el llamador: un fallo de red o de la API
    de Expo no debe romper la acción que la dispara (enviar un mensaje, dar
    like, etc.).
    """
    usuario = Usuario.query.get(usuario_id)
    if not usuario or not usuario.push_token:
        return

    payload = {
        "to": usuario.push_token,
        "title": titulo,
        "body": cuerpo,
        "data": datos or {},
    }

    try:
        requests.post(URL_PUSH_EXPO, json=payload, timeout=3)
    except Exception:
        # Deliberadamente amplio: nada relacionado con enviar una notificación
        # (red, timeout, respuesta inesperada de Expo) debe tumbar la acción
        # que la dispara (enviar un mensaje, dar like, etc.).
        pass
