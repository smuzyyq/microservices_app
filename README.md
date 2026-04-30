# FoodRush

FoodRush is a cloud-deployed food delivery platform built with a microservices architecture. The project was created for Assignment 4 and Assignment 5 and demonstrates:

- microservices implementation
- containerized deployment with Docker Compose
- infrastructure provisioning with Terraform
- monitoring with Prometheus and Grafana
- incident simulation and postmortem analysis

## Repository Contents

This repository includes all required deliverables:

- microservices source code
- frontend application
- `docker-compose.yml`
- Dockerfiles for all services
- Terraform configuration files
- monitoring configuration
- README with setup and deployment instructions

## System Components

### Application Services

- `auth-service` on `8001`
- `product-service` on `8002`
- `order-service` on `8003`
- `user-service` on `8004`
- `chat-service` on `8005`
- `frontend` on `80`

### Monitoring Services

- `prometheus` on `9090`
- `grafana` on `3000`

### Databases

- `auth-db`
- `product-db`
- `order-db`
- `chat-db`

## Architecture

Each backend service follows a simple layered structure:

- `domain` for entities and domain exceptions
- `use_cases` for business logic
- `interfaces` for routers, schemas, and repository contracts
- `infrastructure` for database access, ORM models, and adapters

The frontend is served through Nginx and communicates with backend services through the reverse-proxied `/api/...` routes.

## Main Features

- customer registration and login
- Kazakhstan-themed restaurant catalog
- menu browsing and cart checkout
- saved addresses for order delivery
- customer order history
- courier delivery board
- chat support for order-related communication
- service health and metrics endpoints

## Prerequisites

For local development:

- Docker
- Docker Compose

For Terraform deployment:

- Terraform `>= 1.5.0`
- Google Cloud account
- enabled billing in GCP
- enabled Compute Engine API
- authenticated Google Cloud CLI or equivalent Terraform credentials

## Environment Configuration

Create a `.env` file in the project root.

The fastest option is:

```bash
cp .env.example .env
```

Example configuration:

```env
AUTH_DATABASE_URL=postgresql://foodrush:foodrush123@auth-db:5432/auth_db
PRODUCT_DATABASE_URL=postgresql://foodrush:foodrush123@product-db:5432/product_db
ORDER_DATABASE_URL=postgresql://foodrush:foodrush123@order-db:5432/order_db
USER_DATABASE_URL=postgresql://foodrush:foodrush123@auth-db:5432/auth_db
CHAT_DATABASE_URL=postgresql://foodrush:foodrush123@chat-db:5432/chat_db
JWT_SECRET=foodrush-super-secret
PRODUCT_SERVICE_URL=http://product-service:8002/products
ORDER_SERVICE_URL=http://order-service:8003/orders
POSTGRES_USER=foodrush
POSTGRES_PASSWORD=foodrush123
```

## Local Setup

### 1. Start the Full Stack

```bash
docker compose up -d --build
```

### 2. Verify Running Containers

```bash
docker compose ps
```

### 3. Open the Services

- Frontend: [http://localhost](http://localhost)
- Grafana: [http://localhost:3000](http://localhost:3000)
- Prometheus: [http://localhost:9090](http://localhost:9090)

### 4. Verify Health Endpoints

```bash
curl http://localhost/api/auth/health
curl http://localhost/api/products/health
curl http://localhost/api/orders/health
curl http://localhost/api/users/health
curl http://localhost/api/chat/health
```

## Demo Accounts

The project seeds staff demo users in `auth-service`.

### Seeded Accounts

- Courier:
  - email: `courier@foodrush.kz`
  - password: `Courier123!`
- Admin:
  - email: `admin@foodrush.kz`
  - password: `Admin123!`

### Customer Account

Customers should register through the frontend.

## Docker Compose Services

The project is started from a single `docker-compose.yml` file and includes:

- application services
- PostgreSQL databases
- Prometheus
- Grafana

Useful commands:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
docker compose down
```

## Monitoring

### Prometheus

Prometheus scrapes `/metrics` from:

- `auth-service`
- `product-service`
- `order-service`
- `user-service`
- `chat-service`

### Grafana Dashboard

The Grafana dashboard includes:

- service availability
- healthy targets
- request rate
- 5xx error rate
- P95 latency
- CPU usage
- resident memory

### Alerts

Two Prometheus alerts are configured for `order-service`:

- `OrderServiceDown`
- `OrderServiceDatabaseDisconnected`

The first detects complete service outage. The second detects degraded state when `order-service` is still reachable but has lost database connectivity.

## Terraform Deployment

Terraform is used to provision infrastructure in Google Cloud.

### Provisioned Resources

- one Google Compute Engine virtual machine
- one firewall rule allowing:
  - `22` for SSH
  - `80` for HTTP
  - `3000` for Grafana
  - `9090` for Prometheus
- output values including public IP

### Terraform Files

- `terraform/main.tf`
- `terraform/variables.tf`
- `terraform/outputs.tf`
- `terraform/terraform.tfvars`

### Terraform Commands

```bash
cd terraform
terraform init
terraform plan
terraform apply
terraform output
```

## Cloud Deployment Guide

After Terraform provisions the VM, deploy the application with the following steps.

### 1. Connect to the VM

Use SSH from Google Cloud Console or the `gcloud` CLI.

### 2. Install Docker and Docker Compose

Example commands for Debian 12:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Clone the Repository

```bash
git clone https://github.com/smuzyyq/microservices_app.git
cd microservices_app
```

### 4. Create `.env`

```bash
cp .env.example .env
```

Edit `.env` if needed.

### 5. Start the Platform

```bash
docker compose up -d --build
```

### 6. Verify the Deployment

```bash
docker compose ps
curl http://localhost/api/orders/health
```

Open the public endpoints using the VM public IP:

- `http://<PUBLIC_IP>`
- `http://<PUBLIC_IP>:3000`
- `http://<PUBLIC_IP>:9090`

## Incident Simulation Guide

The assignment incident was simulated by intentionally misconfiguring `ORDER_DATABASE_URL`.

### Before Incident

Verify the system is healthy:

```bash
docker compose ps
curl http://localhost/api/orders/health
```

### Trigger Incident

Break the database connection string in `.env`, for example:

```env
ORDER_DATABASE_URL=postgresql://foodrush:wrongpass@order-db:5432/order_db
```

Restart the affected service:

```bash
docker compose up -d order-service
```

### Validate Incident

```bash
docker compose logs --tail=100 order-service
curl http://localhost/api/orders/health
```

Expected result:

- `order-service` remains reachable
- `/health` returns `degraded`
- `OrderServiceDatabaseDisconnected` eventually fires in Prometheus

### Recovery

Restore the correct `ORDER_DATABASE_URL` and restart the service:

```bash
docker compose up -d order-service
curl http://localhost/api/orders/health
```

## Project Structure

```text
foodrush/
├── frontend/
├── monitoring/
│   ├── grafana/
│   └── prometheus/
├── services/
│   ├── auth/
│   ├── chat/
│   ├── order/
│   ├── product/
│   └── user/
├── terraform/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Notes

- `auth-service` and `user-service` share `auth_db`
- each backend service exposes `/health` and `/metrics`
- `order-service` supports degraded mode when the database is unavailable
- Grafana is provisioned automatically on startup
- Prometheus alert rules are provisioned automatically on startup

## Submission Mapping

This repository matches the assignment deliverables as follows:

- Source Code:
  - microservices implementation
  - frontend application
- Container Configuration:
  - `docker-compose.yml`
  - Dockerfiles
- Infrastructure Code:
  - Terraform configuration files
- Documentation:
  - README setup instructions
  - deployment guide
- Assignment 4:
  - incident simulation
  - postmortem analysis in the final report
- Assignment 5:
  - Terraform implementation and explanation in the final report
- Supporting Evidence:
  - screenshots collected separately for the final PDF report

