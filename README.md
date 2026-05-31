# Microservices Project

A distributed microservices architecture built with FastAPI, Redis, PostgreSQL, and Docker. This project demonstrates secure API gateway routing, JWT-based authentication, asynchronous message processing with Redis streams, and containerized deployment.

## 📋 Project Overview

This project includes four main components:

1. **Auth Service** - User registration, login, and JWT token issuance
2. **Gateway Service** - API gateway with token validation and request forwarding
3. **Inventory Service** - Product catalog, inventory management, and refund event publishing
4. **Payments Service** - Order creation, payment processing, and refund handling

Supporting components:
- **Redis** for object storage and event streams
- **PostgreSQL** for auth database persistence
- **Background consumers** for async inventory and refund processing

## 🏗️ Architecture

```
                ┌────────────┐
                │  Auth API  │
                │  (8003)    │
                └──────┬─────┘
                       │
                       ▼
┌──────────┐   ┌──────────────────────┐   ┌─────────────┐
│ Client   │──▶│ Gateway API (9000)   │──▶│ Inventory   │
│          │   │                      │   │ Service     │
└──────────┘   │                      │   │ (8005)      │
               │                      │   └─────────────┘
               │                      │
               │                      │   ┌─────────────┐
               │                      │──▶│ Payments    │
               │                      │   │ Service     │
               │                      │   │ (8001)      │
               │                      │   └─────────────┘
               │                      │
               │                      │   ┌─────────────┐
               │                      │   │ Redis       │
               │                      │   │ (6379)      │
               │                      │   └─────────────┘
               │
               │                      ┌─────────────┐
               │                      │ Inventory   │
               │                      │ Consumer    │
               │                      └─────────────┘
               │                      ┌─────────────┐
               │                      │ Payments    │
               │                      │ Consumer    │
               │                      └─────────────┘
               ▼
          ┌────────────┐
          │ PostgreSQL │
          │ auth_db    │
          └────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker
- Docker Compose
- Python 3.9+ (for local development)

### Run with Docker Compose

1. Change into the project directory:

```bash
cd microservices2
```

2. Build and start all services:

```bash
docker-compose up --build
```

The application stack will start on these host ports:

- **Gateway:** `http://localhost:9000`
- **Inventory Service:** `http://localhost:8005`
- **Payments Service:** `http://localhost:8001`
- **Auth Service:** `http://localhost:8003`
- **Redis:** `http://localhost:6379`
- **PostgreSQL:** `http://localhost:5433`

3. Verify service availability:

```bash
curl http://localhost:9000/auth/register
curl http://localhost:9000/inventory/products
curl http://localhost:9000/payments/orders
```

## 📦 Services

### Auth Service

**Port:** `8003`

**Features:**
- User registration with hashed passwords
- User login with JWT access token issuance
- PostgreSQL persistence for user accounts

**Endpoints:**
- `POST /register` - Register a new user
- `POST /login` - Authenticate and receive JWT token

### Gateway Service

**Port:** `9000`

**Features:**
- Central routing for inventory, payments, and auth requests
- JWT validation for inventory and payment API calls
- Transparent proxying of request body and headers

**Routes:**
- `POST /auth/{path}` → forwards auth requests to Auth Service
- `GET/POST/DELETE /inventory/{path}` → forwards to Inventory Service
- `GET/POST/DELETE /payments/{path}` → forwards to Payments Service

### Inventory Service

**Host Port:** `8005`

**Features:**
- Product create/read/delete operations
- Uses Redis OM for product modeling
- Publishes `refund_order` events when a product is deleted
- CORS enabled for frontend integration

**Endpoints:**
- `GET /products` - List all products
- `GET /get_products/{pk}` - Get product details by ID
- `POST /create_products` - Create a new product
- `DELETE /delete_products/{pk}` - Delete a product and emit refund event

### Payments Service

**Host Port:** `8001`

**Features:**
- Order creation with inventory validation
- Automatic fee and total calculation
- Background async status updates for orders
- Publishes `order_completed` and `refund_order` events
- Uses Redis OM for order storage
- CORS enabled for frontend integration

**Endpoints:**
- `GET /orders` - List all orders
- `GET /orders/{pk}` - Get an order by ID
- `POST /orders` - Create an order
- `DELETE /delete_orders/{pk}` - Delete an order

### Async Consumers

Two background workers process Redis streams:

- `inventory_consumer` consumes `order_completed` events and decrements inventory quantities
- `payment_consumer` consumes `refund_order` events and sets related pending orders to `refunded`

## 🔄 Workflow

### Order Lifecycle

1. Client requests order creation through Gateway.
2. Payments Service fetches product details from Inventory Service.
3. Order is saved with `pending` status in Redis.
4. Background task waits and updates order status to `completed` or `refunded`.
5. A Redis stream event is published for downstream services.

### Refund Processing

- When a product is deleted, Inventory Service publishes a `refund_order` event.
- Payment consumer listens on the `refund_order` stream.
- Pending orders for the deleted product are marked as `refunded`.
- Inventory consumer also uses `order_completed` events to adjust stock levels.

## 🛠️ Project Structure

```
microservices2/
├── auth/                     # Authentication microservice
│   ├── auth.py               # JWT helpers
│   ├── database.py           # SQLAlchemy PostgreSQL setup
│   ├── dockerfile            # Auth container image
│   ├── main.py               # FastAPI auth app
│   ├── models.py             # SQLAlchemy user model
│   ├── requirements.txt      # Auth dependencies
│   └── schemas.py            # Pydantic request/response schemas
├── gateway/                  # API gateway microservice
│   ├── dockerfile            # Gateway container image
│   └── main.py               # FastAPI proxy app
├── inventory/                # Inventory microservice
│   ├── consumer.py           # Redis stream consumer
│   ├── dockerfile            # Inventory container image
│   ├── main.py               # FastAPI inventory app
│   ├── redis_client.py       # Redis OM connection and product model
│   └── requirements.txt      # Inventory dependencies
├── payments/                 # Payments microservice
│   ├── consumer.py           # Refund stream consumer
│   ├── dockerfile            # Payments container image
│   ├── main.py               # FastAPI payments app
│   ├── redis_client.py       # Redis OM connection and order model
│   ├── requirements.txt      # Payments dependencies
│   └── schemas.py            # Pydantic order schemas
├── docker-compose.yml        # Multi-container orchestration
└── README.md                 # Project documentation
```

## 🔧 Configuration

### Environment Variables

The services use the following environment values in `docker-compose.yml` and `auth/.env`:

- `REDIS_URL` - Redis hostname
- `REDIS_PORT` - Redis port
- `REDIS_PASSWORD` - Redis password for Redis server
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - PostgreSQL database name
- `SECRET_KEY` - JWT signing secret
- `ALGORITHM` - JWT signing algorithm

### Internal Service URLs

Internal container addresses used by services:

- `http://inventory:8000`
- `http://payment:8000`
- `http://auth:8000`

## 🧪 Example Requests

### Auth

```bash
curl -X POST http://localhost:9000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@example.com","password":"secret"}'

curl -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"secret"}'
```

### Inventory via Gateway

```bash
curl -H "Authorization: Bearer <token>" http://localhost:9000/inventory/products
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"name":"Widget","price":25.50,"quantity":50}' \
  http://localhost:9000/inventory/create_products
```

### Payments via Gateway

```bash
curl -H "Authorization: Bearer <token>" http://localhost:9000/payments/orders
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"id":"<product-id>","quantity":2}' \
  http://localhost:9000/payments/orders
```

## 🐛 Troubleshooting

- Ensure Docker and Docker Compose are installed and running
- Confirm required ports are free: `8005`, `8001`, `9000`, `8003`, `6379`, `5433`
- Verify container startup logs:
  - `docker-compose logs gateway`
  - `docker-compose logs inventory`
  - `docker-compose logs payment`
  - `docker-compose logs auth`
- Check Redis authentication and PostgreSQL credentials in `.env`

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

- Verify Redis service is running: `docker-compose ps`
- Check Redis credentials in docker-compose.yml
- Ensure containers can communicate: `docker-compose logs redis`

**Microservice communication errors:**
- Check service names in docker-compose.yml
- Verify service dependencies are ordered correctly
- Check firewall/network settings

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 📄 License

This project is provided as-is for educational purposes.
