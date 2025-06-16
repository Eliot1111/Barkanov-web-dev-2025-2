import re
from flask import abort

SQL_INJECTION_PATTERNS = [
    r"(--|\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC|UNION|OR|AND)\b)",
    r"('|\")",
    r"(;)"
]

def is_safe_input(value: str) -> bool:
    if not isinstance(value, str):
        return True
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return False
    return True

def validate_form_fields(form_data):

    for key, value in form_data.items():
        if not is_safe_input(value):
            abort(400, description=f"Обнаружена потенциальная SQL-инъекция в поле: {key}")
