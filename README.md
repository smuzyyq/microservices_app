# FoodRush

FoodRush is a food delivery microservices skeleton built with Clean Architecture principles. The repository includes five FastAPI services, a static frontend behind Nginx, PostgreSQL databases, Prometheus, Grafana, and Terraform starter files.

## Services

- `auth-service` on `8001`
- `product-service` on `8002`
- `order-service` on `8003`
- `user-service` on `8004`
- `chat-service` on `8005`
- `frontend` on `80`
- `prometheus` on `9090`
- `grafana` on `3000`

## Architecture

Each backend service follows a simple Clean Architecture layout:

- `domain`: core entities and domain exceptions
- `use_cases`: application business rules
- `interfaces`: routers, schemas, and repository contracts
- `infrastructure`: database, models, and adapters

## Quick Start

1. Copy `.env.example` to `.env`.
2. Build and start the stack:

```bash
docker compose up --build
```

3. Open:

- Frontend: `http://localhost`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Notes

- `auth-service` and `user-service` share `auth_db`.
- Each service exposes `/health` and `/metrics`.
- The starter repositories are intentionally lightweight and ready for real persistence logic later.
