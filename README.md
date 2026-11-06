# Урок 43 — проектирование REST API

Сервис: бронирование барбершопа. Ресурсы: мастера (`masters`), услуги (`services`), клиенты (`clients`) и записи (`appointments`). Время передаётся в ISO 8601 с часовым поясом, например `2026-11-10T14:00:00+05:00`. Цена указана целым числом в сумах.

## Уровень 1. Исправление URL

| Было | Стало | Смысл |
|---|---|---|
| `/getAllUsers` | `GET /users` | Получить список пользователей |
| `/createUser` | `POST /users` | Создать пользователя; данные в JSON-теле |
| `/user/delete?id=7` | `DELETE /users/7` | Удалить пользователя 7 |
| `/updateUserEmail/7` | `PATCH /users/7` | Изменить email; тело `{"email":"new@example.com"}` |
| `/getOrdersOfUser?user=3` | `GET /users/3/orders` | Получить заказы пользователя 3 |
| `/products/search_by_category/phones` | `GET /products?category=phones` | Отфильтровать товары по категории |

## Уровень 2. Дизайн API

Тело запроса и ответ в таблице — примеры JSON. `—` означает отсутствие тела. В примерах существующие ID заранее созданы. `404` означает, что ресурс с указанным ID не найден. `400` означает неверные поля или значения. В реальном приложении создание записи дополнительно проверяет свободное время мастера; занятый слот возвращает `409`.

| Метод и URL | Тело запроса | Пример успешного ответа | Коды |
|---|---|---|---|
| `GET /masters` | — | `[{"id":1,"name":"Азиз"}]` | `200` |
| `GET /masters/1` | — | `{"id":1,"name":"Азиз"}` | `200`, `404` |
| `POST /masters` | `{"name":"Азиз"}` | `{"id":1,"name":"Азиз"}` | `201`, `400` |
| `PATCH /masters/1` | `{"name":"Сардор"}` | `{"id":1,"name":"Сардор"}` | `200`, `400`, `404` |
| `DELETE /masters/1` | — | — | `204`, `404`, `409` |
| `GET /services` | — | `[{"id":1,"name":"Мужская стрижка","duration_minutes":45,"price_uzs":80000}]` | `200` |
| `GET /services/1` | — | `{"id":1,"name":"Мужская стрижка","duration_minutes":45,"price_uzs":80000}` | `200`, `404` |
| `POST /services` | `{"name":"Оформление бороды","duration_minutes":30,"price_uzs":50000}` | `{"id":2,"name":"Оформление бороды","duration_minutes":30,"price_uzs":50000}` | `201`, `400` |
| `PATCH /services/1` | `{"price_uzs":90000}` | `{"id":1,"name":"Мужская стрижка","duration_minutes":45,"price_uzs":90000}` | `200`, `400`, `404` |
| `DELETE /services/1` | — | — | `204`, `404`, `409` |
| `GET /clients` | — | `[{"id":1,"name":"Али","phone":"+998901234567"}]` | `200` |
| `GET /clients/1` | — | `{"id":1,"name":"Али","phone":"+998901234567"}` | `200`, `404` |
| `POST /clients` | `{"name":"Али","phone":"+998901234567"}` | `{"id":1,"name":"Али","phone":"+998901234567"}` | `201`, `400` |
| `PATCH /clients/1` | `{"phone":"+998901234568"}` | `{"id":1,"name":"Али","phone":"+998901234568"}` | `200`, `400`, `404` |
| `GET /appointments` | — | `[{"id":1,"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T14:00:00+05:00","status":"booked"}]` | `200` |
| `GET /appointments?date=2026-11-10&master_id=1` | — | `[{"id":1,"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T14:00:00+05:00","status":"booked"}]` | `200`, `400` |
| `GET /appointments/1` | — | `{"id":1,"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T14:00:00+05:00","status":"booked"}` | `200`, `404` |
| `GET /masters/1/appointments` | — | `[{"id":1,"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T14:00:00+05:00","status":"booked"}]` | `200`, `404` |
| `GET /clients/1/appointments` | — | `[{"id":1,"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T14:00:00+05:00","status":"booked"}]` | `200`, `404` |
| `POST /appointments` | `{"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T14:00:00+05:00"}` | `{"id":1,"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T14:00:00+05:00","status":"booked"}` | `201`, `400`, `404`, `409` |
| `PATCH /appointments/1` | `{"starts_at":"2026-11-10T15:00:00+05:00"}` | `{"id":1,"master_id":1,"service_id":1,"client_id":1,"starts_at":"2026-11-10T15:00:00+05:00","status":"booked"}` | `200`, `400`, `404`, `409` |
| `DELETE /appointments/1` | — | — | `204`, `404` |

Фильтры `date` и `master_id` можно применять отдельно или вместе. Пустой результат — `200` и `[]`. При `DELETE` с кодом `204` тело ответа пустое. Ошибки имеют единый формат, например `{"error":"Not found","code":404}`. Каждый запрос должен передавать нужные данные самостоятельно; для защищённой версии API это включает токен в заголовке `Authorization`.

## Уровень 3. Реализация услуг

В `app.py` реализованы пять маршрутов ресурса услуг: `GET /services`, `GET /services/<id>`, `POST /services`, `PATCH /services/<id>`, `DELETE /services/<id>`. Пятый маршрут позволяет получить созданную услугу по `Location` из ответа `POST`. Остальные маршруты из таблицы — проект API, а не реализованный код. Хранилище учебное, в памяти: после перезапуска изменения исчезают. Начальные услуги имеют ID 1 и 2.

### Запуск

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Сервер слушает `http://127.0.0.1:5000`. Для проверки в Postman импортируйте `postman_collection.json` и запустите запросы по порядку. Пример ручной проверки:

```bash
curl -i http://127.0.0.1:5000/services
curl -i -X POST http://127.0.0.1:5000/services -H 'Content-Type: application/json' -d '{"name":"Детская стрижка","duration_minutes":40,"price_uzs":70000}'
curl -i -X PATCH http://127.0.0.1:5000/services/3 -H 'Content-Type: application/json' -d '{"price_uzs":75000}'
curl -i -X DELETE http://127.0.0.1:5000/services/3
curl -i http://127.0.0.1:5000/services/3
```

Ожидаемые коды по порядку: `200`, `201`, `200`, `204`, `404`. Неверный JSON или поля дают JSON-ошибку `400`; неверный `Content-Type` — `415`.

### Репозиторий

Ссылка на репозиторий: https://github.com/abubakr-isco/-REST-API
