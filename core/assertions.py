class TestAssertionError(Exception):
    pass


def assert_status(response, expected_status):
    if isinstance(expected_status, int):
        expected_status = [expected_status]

    if response.status_code not in expected_status:
        raise TestAssertionError(
            f"Se esperaba HTTP {expected_status}, "
            f"pero se recibió HTTP {response.status_code}. "
            f"Respuesta: {response.text[:1500]}"
        )


def assert_json(response):
    try:
        return response.json()
    except ValueError:
        raise TestAssertionError(
            "La respuesta del servidor no contiene JSON válido."
        )


def assert_true(condition, message):
    if not condition:
        raise TestAssertionError(message)


def assert_equal(actual, expected, message=""):
    if actual != expected:
        raise TestAssertionError(
            f"{message}. Esperado: {expected}. Recibido: {actual}"
        )


def assert_not_none(value, message):
    if value is None:
        raise TestAssertionError(message)