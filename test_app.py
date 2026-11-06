"""Проверка основных HTTP-методов и единого формата ошибок."""

import unittest

import app as service_app


class ServicesApiTest(unittest.TestCase):
    def setUp(self):
        service_app.services.clear()
        service_app.services.update({
            1: {"id": 1, "name": "Мужская стрижка", "duration_minutes": 45, "price_uzs": 80000}
        })
        service_app.next_id = 2
        self.client = service_app.app.test_client()

    def test_service_lifecycle(self):
        response = self.client.get("/services")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

        response = self.client.post("/services", json={
            "name": "Оформление бороды", "duration_minutes": 30, "price_uzs": 50000
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["Location"], "/services/2")
        self.assertEqual(self.client.get("/services/2").json["name"], "Оформление бороды")

        response = self.client.patch("/services/2", json={"price_uzs": 55000})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["price_uzs"], 55000)

        self.assertEqual(self.client.delete("/services/2").status_code, 204)
        response = self.client.get("/services/2")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Not found", "code": 404})

    def test_validation_errors_are_json(self):
        response = self.client.post("/services", json={"name": "Новая услуга"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["code"], 400)

        response = self.client.patch("/services/1", json={"price_uzs": -1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["code"], 400)

        response = self.client.post("/services", data="plain text")
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.json["code"], 415)


if __name__ == "__main__":
    unittest.main()
