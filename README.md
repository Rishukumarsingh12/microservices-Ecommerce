# Microservices Project

A distributed microservices architecture built with FastAPI, Redis, and Docker. This project demonstrates inter-service communication, asynchronous message processing, and containerized deployment.

## 📋 Project Overview

This project consists of two main microservices:

1. **Inventory Service** - Manages product catalog and inventory
2. **Payments Service** - Manages orders and payment processing

Both services communicate asynchronously through Redis and expose REST APIs for client interaction.

## 🏗️ Architecture

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────┐
│  Inventory API  │───────▶│  Payments API    │───────▶│  Redis  │
│  (Port 8000)    │        │  (Port 8001)     │        │ Queue   │
└─────────────────┘        └──────────────────┘        └─────────┘
        │                          │                         │
        ▼                          ▼                         ▼
┌─────────────────┐        ┌──────────────────┐        ┌─────────┐
│ Inventory       │        │ Payments         │        │ Refund  │
│ Consumer        │        │ Consumer         │        │ Events  │
└─────────────────┘        └──────────────────┘        └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker
- Docker Compose
- Python 3.9+ (for local development)

### Installation & Running

1. Clone the repository:
```bash
cd microservices2
```

2. Build and run all services with Docker Compose:
```bash
docker-compose up --build
```

This will start:
- **Inventory Service** on `http://localhost:8000`
- **Payments Service** on `http://localhost:8001`
- **Redis** on `localhost:6379`
- **Background Consumers** for processing async events

3. Verify services are running:
```bash
curl http://localhost:8000/products
curl http://localhost:8001/orders
```

## 📦 Services

### Inventory Service

**Port:** 8000

**Endpoints:**

- `GET /products` - Get all products
- `POST /create_products` - Create a new product
- `GET /get_products/{pk}` - Get product by ID
- `DELETE /delete_products/{pk}` - Delete a product (triggers refund event)

**Technologies:** FastAPI, Redis-OM, Redis

### Payments Service

**Port:** 8001

**Endpoints:**

- `GET /orders` - Get all orders
- `GET /orders/{pk}` - Get order by ID
- `POST /orders` - Create a new order
- `DELETE /delete_orders/{pk}` - Delete an order

**Technologies:** FastAPI, Redis-OM, Redis, Background Tasks

## 🔄 Message Flow

1. **Order Creation Flow:**
   - Client sends order request to Payments API
   - Payments service queries Inventory service for product details
   - Order is created and stored in Redis
   - Payment consumer processes the order asynchronously

2. **Refund Flow:**
   - When a product is deleted from Inventory, a refund event is published
   - Event is placed on the `refund-order` Redis stream
   - Payment consumer listens and processes refund events

## 🛠️ Development

### Project Structure

```
microservices2/
├── docker-compose.yml         # Service orchestration
├── inventory/                 # Inventory microservice
│   ├── main.py               # FastAPI application
│   ├── consumer.py           # Async message consumer
│   ├── redis_client.py       # Redis client & models
│   ├── dockerfile            # Container image
│   └── requirements.txt       # Python dependencies
├── payments/                  # Payments microservice
│   ├── main.py               # FastAPI application
│   ├── consumer.py           # Async message consumer
│   ├── redis_client.py       # Redis client & models
│   ├── dockerfile            # Container image
│   └── requirements.txt       # Python dependencies
└── README.md                 # This file
```

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd inventory
pip install -r requirements.txt
```

3. Run a service locally:
```bash
uvicorn main:app --reload --port 8000
```

## 🔐 Configuration

### Redis Connection

- **Host:** redis (from docker-compose)
- **Port:** 6379
- **Password:** GGWCEQ4FncKvWWYpjWZSJs5d5uGUxdXw

Environment variables (set in docker-compose.yml):
- `REDIS_URL` - Redis host
- `REDIS_PORT` - Redis port

### CORS Configuration

Services allow requests from `http://localhost:3000` for frontend integration.

## 📝 Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **redis-om** - Redis object mapping
- **python-dotenv** - Environment variables
- **requests** - HTTP client for inter-service communication

## 🧪 Testing

Test inventory endpoints:
```bash
# Get all products
curl http://localhost:8000/products

# Create a product
curl -X POST http://localhost:8000/create_products \
  -H "Content-Type: application/json" \
  -d '{"name":"Product1","price":99.99,"quantity":10}'

# Get product by ID
curl http://localhost:8000/get_products/{id}
```

Test payment endpoints:
```bash
# Get all orders
curl http://localhost:8001/orders

# Create an order
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{"id":"product-id"}'
```

## 🐛 Troubleshooting

**Services won't start:**
- Ensure Docker and Docker Compose are installed
- Check port availability (8000, 8001, 6379)
- View logs: `docker-compose logs`

**Redis connection issues:**
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
