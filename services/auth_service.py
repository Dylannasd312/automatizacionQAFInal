import os

from services.api_client import APIClient


def autenticar():

    base_url = os.getenv(
        "API_BASE_URL"
    )

    username = os.getenv(
        "API_USERNAME"
    )

    password = os.getenv(
        "API_PASSWORD"
    )

    timeout = int(
        os.getenv("REQUEST_TIMEOUT", "30")
    )

    if not all([base_url, username, password]):
        raise Exception(
            "Faltan credenciales o URL de conexión en .env"
        )

    cliente = APIClient(
        base_url,
        timeout
    )

    cliente.login(
        username,
        password
    )

    return cliente