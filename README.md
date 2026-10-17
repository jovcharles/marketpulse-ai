# MarketPulse AI

This is my first real attempt at building an AI-powered automation/data project.

It is not meant to be presented as a finished product or a polished startup app. This repo is more of a hands-on learning project: a place to explore data pipelines, AI workflows, automation, and database-driven experimentation while I build up my understanding of the technology.

The goal is to learn by doing: fetch market data, clean and transform it, store it in a database, and gradually expand into smarter analysis and AI-assisted features.

## Overview

MarketPulse AI is a small experimental project focused on collecting and processing market/crypto data. The current pipeline:

- pulls price data for selected symbols
- cleans and validates the raw records
- loads the results into PostgreSQL
- keeps the project structured so future AI and analytics features can build on top of it

At the moment, this is a foundational prototype rather than a production-ready platform.

## Why this project exists

This is a practice repo for learning:

- Python data engineering workflows
- ETL-style pipelines
- PostgreSQL storage and schema design
- AI automation ideas and experimentation
- building a base project that can grow over time

The spirit of the project is learning by iteration, not shipping a finished SaaS product.

## Current architecture

The project is organized around a basic data pipeline:

- `pipeline/extractors/` - fetches raw market data
- `pipeline/transformers/` - cleans and validates incoming records
- `pipeline/loaders/` - writes processed data into PostgreSQL
- `database/` - database schema and related SQL
- `docker-compose.yml` - local Postgres setup

This is intentionally simple and easy to extend.

## Project structure

```text
marketpulse-ai/
├── .env
├── docker-compose.yml
├── requirements.txt
├── README.md
├── database/
│   └── schema.sql
├── pipeline/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── market_date.py
│   │   └── news_extractor.py
│   ├── transformers/
│   │   └── prices.py
│   ├── loaders/
│   │   ├── postgres.py
│   │   └── prices.py
│   └── tests/
│       └── test_prices.py
├── backend/
├── frontend/
└── docs/
```

## What is working right now

The current setup can:

- fetch historical crypto price data from Yahoo Finance
- normalize timestamps and numeric fields
- validate suspicious/invalid rows
- insert records into a PostgreSQL table with a symbol + timestamp primary key
- run locally using Docker for Postgres

## Getting started

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start local PostgreSQL

```bash
docker compose up -d
```

This starts a local Postgres instance using the configuration in `docker-compose.yml`.

### 4. Configure environment variables

The project expects a `DATABASE_URL` value in the environment. A sample `.env` is included, and it should be adjusted to match your local setup.

Example:

```env
DATABASE_URL=postgresql://marketpulse:local_dev_password@localhost:5433/marketpulse
```

### 5. Run the pipeline

```bash
python pipeline/main.py
```

This will:

- fetch sample market data
- transform it
- initialize the database schema
- insert the data into PostgreSQL

## Database schema

The main table currently defined in `database/schema.sql` stores market price records:

- `symbol`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

This is built as a simple foundation for future analytics and AI-driven data work.

## Status and expectations

This project is currently best described as:

- an early-stage learning project
- a practical experimentation ground
- a foundation for AI + automation ideas
- not a finished application or production system

The long-term plan is to keep learning and layering in more features, but the current codebase should be treated as a prototype and a working sandbox, not a polished product.

## Possible next steps

Some ideas for where this could go next:

- add more market data sources
- build a dashboard or frontend
- store news or sentiment data alongside prices
- add embeddings and semantic search
- use AI to summarize market conditions
- automate recurring analysis workflows

## Final note

This repo reflects my first take on AI automation and data-driven experimentation. It is intentionally simple, honest, and practical. The point is to learn and improve over time, not to pretend the project is already complete.
I used ChatGPT and various documentations for this as a guide.