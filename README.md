# 🍔 TastyGo — Online Food Ordering System

A full-stack food ordering web app: Flask + SQLite backend, vanilla JS frontend,
Dockerized, with Jenkins pipeline and Terraform infra scaffolding for AWS EC2 deployment.

**This is a real, working application** — tested end-to-end (menu, cart, checkout,
order history) before delivery, not just a spec.

## Features
- Browse menu by category
- Add/remove items, adjust quantity in cart
- Place an order with delivery details
- View order history with live status badges
- REST API backing everything (see below)

## Tech Stack
- **Backend:** Python Flask + Flask-SQLAlchemy (SQLite)
- **Frontend:** HTML/CSS/vanilla JS (no build step needed)
- **Containerization:** Docker
- **CI/CD:** Jenkins (pipeline provided in `jenkins/Jenkinsfile`)
- **Infra:** Terraform (AWS VPC + EC2, in `terraform/`)

## Run Locally (fastest way to see it working)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser. The database (`food_ordering.db`)
and menu seed data are created automatically on first run.

## Run with Docker

```bash
docker build -t tastygo:latest .
docker run -p 5000:5000 tastygo:latest
```

Or with Docker Compose:

```bash
docker-compose up --build
```

## API Reference

| Method | Endpoint                     | Description                  |
|--------|-------------------------------|-------------------------------|
| GET    | `/api/health`                 | Health check                  |
| GET    | `/api/menu`                   | List menu items (optional `?category=`) |
| GET    | `/api/menu/<id>`              | Get single menu item          |
| POST   | `/api/menu`                   | Add a menu item                |
| GET    | `/api/orders`                 | List all orders                |
| GET    | `/api/orders/<id>`            | Get single order               |
| POST   | `/api/orders`                 | Place a new order              |
| PATCH  | `/api/orders/<id>/status`     | Update order status            |

### Example: place an order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Zubeir",
    "customer_phone": "9876543210",
    "address": "Chennai",
    "items": [{"menu_item_id": 1, "quantity": 2}]
  }'
```

## Project Structure
```
food-ordering-system/
├── backend/
│   ├── app.py            # Flask app + models + all routes
│   ├── requirements.txt
│   └── food_ordering.db  # created at runtime, gitignored
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── Dockerfile
├── docker-compose.yml
├── jenkins/
│   └── Jenkinsfile
├── terraform/
│   └── main.tf
└── README.md
```

## Deploying to AWS EC2 (for your DevOps submission)
1. `cd terraform && terraform init && terraform apply` — provisions VPC, subnet,
   security group, and an EC2 instance (edit `main.tf` with your key pair name and AMI first).
2. SSH into the instance, install Docker, then:
   ```bash
   docker run -d -p 80:5000 --restart unless-stopped your-dockerhub-user/tastygo:latest
   ```
3. Push your image to DockerHub first: `docker push your-dockerhub-user/tastygo:latest`.

## Notes for the assignment write-up
- Screenshots to capture at each stage are listed in the original day-wise plan you
  already have — this repo gives you the actual artifacts (code running, API responses,
  Docker build output, etc.) to screenshot.
- The Terraform and Jenkinsfile here are real starting templates, not tested against
  a live AWS account — update `main.tf`'s AMI ID/region/key name for your account before
  running `terraform apply`.
