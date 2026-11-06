"""Учебный REST API услуг барбершопа (данные хранятся в памяти)."""

from flask import Flask, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

services = {
    1: {"id": 1, "name": "Мужская стрижка", "duration_minutes": 45, "price_uzs": 80000},
    2: {"id": 2, "name": "Оформление бороды", "duration_minutes": 30, "price_uzs": 50000},
}
next_id = 3
FIELDS = {"name", "duration_minutes", "price_uzs"}


def error(message, code):
    return {"error": message, "code": code}, code


def read_body():
    if not request.is_json:
        return None, error("Content-Type must be application/json", 415)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error("Expected a JSON object", 400)
    return data, None


def validate(data, *, partial=False):
    if not data or not partial and set(data) != FIELDS:
        return "Required fields: name, duration_minutes, price_uzs"
    if set(data) - FIELDS:
        return "Unknown field"
    if "name" in data and (not isinstance(data["name"], str) or not data["name"].strip()):
        return "name must be a non-empty string"
    for field in ("duration_minutes", "price_uzs"):
        if field in data and (type(data[field]) is not int or data[field] <= 0):
            return f"{field} must be a positive integer"
    return None


@app.get("/services")
def list_services():
    return list(services.values()), 200


@app.get("/services/<int:service_id>")
def get_service(service_id):
    if service_id not in services:
        return error("Not found", 404)
    return services[service_id], 200


@app.post("/services")
def create_service():
    global next_id
    data, problem = read_body()
    if problem:
        return problem
    message = validate(data)
    if message:
        return error(message, 400)
    service = {"id": next_id, **data, "name": data["name"].strip()}
    services[next_id] = service
    next_id += 1
    return service, 201, {"Location": f"/services/{service['id']}"}


@app.patch("/services/<int:service_id>")
def update_service(service_id):
    if service_id not in services:
        return error("Not found", 404)
    data, problem = read_body()
    if problem:
        return problem
    message = validate(data, partial=True)
    if message:
        return error(message, 400)
    if "name" in data:
        data["name"] = data["name"].strip()
    services[service_id].update(data)
    return services[service_id], 200


@app.delete("/services/<int:service_id>")
def delete_service(service_id):
    if service_id not in services:
        return error("Not found", 404)
    del services[service_id]
    return "", 204


@app.errorhandler(HTTPException)
def handle_http_error(exc):
    messages = {404: "Not found", 405: "Method not allowed"}
    return error(messages.get(exc.code, exc.name), exc.code)


if __name__ == "__main__":
    app.run()
