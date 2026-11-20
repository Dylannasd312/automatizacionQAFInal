import requests
import json
import re
from pathlib import Path


class APIClient:

    def __init__(self, base_url, timeout=30):

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        self.token = None

        self.evidencias = Path("evidencias")
        self.evidencias.mkdir(exist_ok=True)

        self.contador = 0

    def login(self, username, password):

        response = self.request(
            "POST",
            "login",
            data={
                "username": username,
                "password": password
            },
            guardar=False
        )

        if response.status_code != 200:
            raise Exception(
                f"Error de autenticación: HTTP "
                f"{response.status_code}: {response.text}"
            )

        data = response.json()

        self.token = data.get("token")

        if not self.token:
            raise Exception(
                "Laravel no devolvió el token de Sanctum."
            )

        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })

        self.guardar_evidencia(
            "LOGIN",
            response
        )

        print("Autenticación correcta.")
        print("Token Sanctum obtenido correctamente.")

        return data

    def request(
        self,
        method,
        endpoint,
        data=None,
        guardar=True
    ):

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        response = self.session.request(
            method=method,
            url=url,
            json=data,
            timeout=self.timeout
        )

        if guardar:
            self.guardar_evidencia(
                endpoint,
                response,
                method,
                data
            )

        return response

    def get(self, endpoint):
        return self.request("GET", endpoint)

    def post(self, endpoint, data=None):
        return self.request("POST", endpoint, data)

    def put(self, endpoint, data=None):
        return self.request("PUT", endpoint, data)

    def patch(self, endpoint, data=None):
        return self.request("PATCH", endpoint, data)

    def guardar_evidencia(
        self,
        nombre,
        response,
        method="POST",
        request_data=None
    ):

        self.contador += 1

        nombre_seguro = re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            nombre
        )

        archivo = (
            self.evidencias /
            f"{self.contador:03d}_{nombre_seguro}.json"
        )

        datos = {

            "fecha": __import__("datetime").datetime.now().isoformat(),

            "metodo": method,

            "endpoint": nombre,

            "request": self.redactar(request_data),

            "status_code": response.status_code,

            "response": self.redactar(
                self.obtener_respuesta(response)
            )
        }

        with open(archivo, "w", encoding="utf-8") as file:

            json.dump(
                datos,
                file,
                indent=4,
                ensure_ascii=False
            )

    @staticmethod
    def obtener_respuesta(response):

        try:
            return response.json()

        except ValueError:
            return response.text[:5000]

    @staticmethod
    def redactar(data):

        campos_sensibles = {
            "password", "token", "authorization", "ci", "access_token",
            "nombres", "nombre", "apellido_paterno", "apellido_materno",
            "apellidos", "fecha_nacimiento", "telefono", "telefono_emergencia",
            "correo", "email", "direccion", "contacto_emergencia",
            "diagnostico", "tratamiento", "motivo_consulta",
            "enfermedad_actual", "observaciones", "indicaciones"
        }

        if isinstance(data, dict):

            return {
                key: (
                    "[REDACTADO]"
                    if key.lower() in campos_sensibles
                    else APIClient.redactar(value)
                )
                for key, value in data.items()
            }

        if isinstance(data, list):

            return [
                APIClient.redactar(item)
                for item in data
            ]

        return data