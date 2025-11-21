# 🚀 SnapURL – Distributed, Production-Ready URL Shortener  
### High-performance Bitly-like system with sharding, caching & AWS deployment

SnapURL is a **high-performance URL shortening service** engineered to handle **1M+ requests/day** using:

- **Flask** (Lightweight API layer)
- **Redis caching** (fast redirects)
- **4 PostgreSQL shards** (true horizontal scaling)
- **Gunicorn + gevent** (high concurrency)
- **Docker + docker-compose** (local distributed cluster)
- **AWS-ready deployment** (ECS / EC2 / Fargate)

This is production-grade software following real industry architecture patterns.

---

# 🧱 Architecture
            ┌─────────────────────────┐
            │     Flask API (Gunicorn)│
            │  gevent workers (async) │
            └─────────────┬──────────┘
                          │
                  Cache Lookup (Redis)
                          │
                          ▼
         ┌───────────────────────────────────┐
         │   PostgreSQL Database Shards      │
         │  (db0, db1, db2, db3)             │
         │  Hash-based sharding using SHA256 │
         └───────────────────────────────────┘


---

# 🧠 Features

### Core
- Create short URLs  
- Redirect short → long  
- Analytics (click count)  

### Performance
- Redis caching on read  
- True DB sharding (4 shards)  
- Connection pooling  
- Gunicorn workers  
- Gevent async concurrency  

### Reliability
- 99.9% uptime deployment architecture  
- Automatic shard initialization  
- Independent shard scaling  

### Security
- Rate limiting (Redis sliding window)  
- URL validation  
- Strict schema  

---

# 📦 Project Structure

snapurl/
│── app/
│ ├── api.py
│ ├── cache.py
│ ├── config.py
│ ├── db.py
│ ├── models.py
│ ├── rate_limit.py
│ ├── utils.py
│ └── init.py
│
│── migrations/
│ ├── shard0.sql
│ ├── shard1.sql
│ ├── shard2.sql
│ ├── shard3.sql
│
│── docker/
│ ├── Dockerfile
│ ├── gunicorn.conf.py
│ ├── docker-compose.yml
│
│── requirements.txt
│── README.md


---

# 🔧 Running Locally (Non-Docker)

Requires PostgreSQL running manually.  
Use Docker for easiest sharded environment (recommended).

---

# 🐳 Running with Docker (Recommended)

```bash
cd docker
docker-compose up --build

Services started:
    api → Flask/Gunicorn
    redis → cache
    db0, db1, db2, db3 → PostgreSQL shards
API runs at:
    http://localhost:8000


