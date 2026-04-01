# Odoo 19 Community — Docker Setup Guide

## Prerequisites

- Docker Desktop installed and running
- At least 4 GB RAM available for containers

## Quick Start

```bash
cd "Gold tier/odoo"

# 1. Copy environment file
cp .env.example .env

# 2. Start Odoo + PostgreSQL
docker compose up -d

# 3. Wait ~60 seconds for Odoo to initialize, then open:
#    http://localhost:8069
```

## First-Time Database Setup

1. Open **http://localhost:8069** in your browser
2. You will see the **Database Manager** page
3. Fill in:
   - **Master Password:** `odoo_master_2026`
   - **Database Name:** `ai_employee`
   - **Email:** your email
   - **Password:** your login password
   - **Language:** English
   - **Country:** your country
4. Check **"Demo data"** if you want sample data (recommended for testing)
5. Click **Create Database** — this takes 1-2 minutes

## Install Required Modules

After database creation, go to **Apps** and install:

1. **Accounting** (account) — core accounting, invoicing, chart of accounts
2. **Contacts** (contacts) — partner/customer management
3. **Invoicing** (account) — if not bundled with Accounting
4. **Sales** (sale_management) — optional, for sales orders

## Enable JSON-RPC API Access

The JSON-RPC API is enabled by default on Odoo 19. Test it:

```bash
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "common",
      "method": "version",
      "args": []
    },
    "id": 1
  }'
```

## Stopping / Restarting

```bash
# Stop
docker compose down

# Restart (data persists in volumes)
docker compose up -d

# Full reset (WARNING: deletes all data)
docker compose down -v
```

## Connection Details for AI Employee

| Setting        | Value                          |
|----------------|--------------------------------|
| URL            | `http://localhost:8069`        |
| Database       | `ai_employee`                 |
| JSON-RPC       | `http://localhost:8069/jsonrpc`|
| XML-RPC        | `http://localhost:8069/xmlrpc` |
| Default User   | (your email from setup)       |
| Default Pass   | (your password from setup)    |

These values go in the Gold tier `.env` file as `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`.
