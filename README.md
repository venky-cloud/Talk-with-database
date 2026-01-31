<div align="center">
  <h1>🗣️ Cognit Sphere</h1>
  <p>An intelligent AI assistant that lets you interact with your databases using natural language</p>
  
  [![Status](https://img.shields.io/badge/status-active-success.svg?style=for-the-badge)]()
  [![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)](/LICENSE)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)
  
  [![Backend](https://img.shields.io/badge/FastAPI-009485?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Frontend](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
  [![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
  [![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)

  [![GitHub stars](https://img.shields.io/github/stars/sukumar-cloud/Talk-with-database?style=social)](https://github.com/sukumar-cloud/Talk-with-database/stargazers)
  [![GitHub forks](https://img.shields.io/github/forks/sukumar-cloud/Talk-with-database?style=social)](https://github.com/sukumar-cloud/Talk-with-database/network/members)
  [![GitHub issues](https://img.shields.io/github/issues/sukumar-cloud/Talk-with-database)](https://github.com/sukumar-cloud/Talk-with-database/issues)
</div>

## ✨ Features

<div align="center">
  <img src="https://img.icons8.com/color/96/000000/database-export.png" alt="Database Query" width="48"/>
  <img src="https://img.icons8.com/color/96/000000/chatbot.png" alt="AI Chat" width="48"/>
  <img src="https://img.icons8.com/color/96/000000/visualization-skill.png" alt="Visualization" width="48"/>
  <img src="https://img.icons8.com/color/96/000000/security-checked.png" alt="Security" width="48"/>
</div>

- **Natural Language to SQL** - Convert plain English to optimized SQL queries
- **Multi-Database Support** - Works with both SQL and NoSQL databases
- **Interactive Schema Visualization** - Visual ER diagrams and schema exploration
- **AI-Powered Chat** - Get database insights through natural conversation
- **Query Validation** - Safe execution with built-in validation
- **Modern UI** - Sleek, responsive interface with dark/light themes

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ & npm/yarn
- Python 3.10+
- MySQL 8.0+ (for SQL features)
- MongoDB (optional, for NoSQL features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sukumar-cloud/Talk-with-database.git
   cd Talk-with-database
   ```

2. **Set up backend**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Create `.env` file in the `backend` directory:
   ```env
   DB_TYPE=mysql
   DB_URI=mysql+pymysql://user:password@localhost:3306/your_database
   MONGODB_URI=mongodb://localhost:27017/  # Optional
   ```

4. **Set up frontend**
   ```bash
   cd ../project
   npm install
   ```

5. **Run the application**
   - Backend: `uvicorn fastapi_app.main:app --reload`
   - Frontend: `npm run dev`

   Open [http://localhost:5173](http://localhost:5173) in your browser.

## 🖥️ Screenshots

| Feature | Preview |
|---------|---------|
| **Chat Interface** | ![Chat Interface](https://via.placeholder.com/600x400/2d3748/ffffff?text=Chat+Interface) |
| **Schema Visualization** | ![Schema Visualization](https://via.placeholder.com/600x400/2d3748/ffffff?text=Schema+Visualization) |
| **Query Workbench** | ![Query Workbench](https://via.placeholder.com/600x400/2d3748/ffffff?text=Query+Workbench) |

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit
- **UI Components**: Headless UI, Lucide Icons
- **Visualization**: React Flow, D3.js

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MySQL, MongoDB
- **ORM**: SQLAlchemy, PyMongo
- **AI/ML**: Transformers, spaCy
- **API Docs**: Swagger UI, ReDoc

## 📚 Documentation

For detailed documentation, please visit our [Wiki](https://github.com/sukumar-cloud/Talk-with-database/wiki).

### API Reference

Explore the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing backend framework
- [React](https://reactjs.org/) for the frontend library
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
- All the amazing open-source libraries and tools we depend on

---

<div align="center">
  Made with ❤️ by [Your Name] | [![Twitter](https://img.icons8.com/color/24/000000/twitter--v1.png)](https://twitter.com/yourhandle) [![LinkedIn](https://img.icons8.com/color/24/000000/linkedin.png)](https://linkedin.com/in/yourprofile)
</div>

# Talk-with-database
An AI-powered assistant to talk to your databases using natural language. It supports intent understanding, SQL generation, validation, ranking, and execution. A modern React UI provides a chat experience and database workbenches.

![status](https://img.shields.io/badge/status-active-brightgreen)
![backend](https://img.shields.io/badge/backend-FastAPI-009485)
![frontend](https://img.shields.io/badge/frontend-React-61DAFB)
![license](https://img.shields.io/badge/license-Custom-lightgrey)

> Tip: Use the Quick Links below to jump directly to what you need.

## Quick Links
- **[Run Backend](#backend-setup)**
- **[Run Frontend](#frontend-setup)**
- **[Try the Chat API (cURL)](#api-playground)**
- **[Swagger Docs](#api-documentation)** (`/docs`)
- **[Troubleshooting](#troubleshooting)**

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [API Documentation](#api-documentation)
- [API Playground](#api-playground)
- [Using the Chatbot](#using-the-chatbot)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🧠 Features
- **Natural language to SQL**: Generate safe, executable queries from user prompts.
- **Safety & ranking**: Validate generated SQL and rank candidates before execution.
- **Execution & results**: Run queries and return concise results.
- **Schema inspection**: Inspect MySQL schema (and MongoDB via dedicated routes).
- **Chat UI**: Friendly chatbot page with loading/error states.

## 🏗️ Architecture
- **Frontend**: React + Vite + Tailwind (`project/`)
- **Backend**: FastAPI (`backend/fastapi_app/`)
- **Routers**: `nlu`, `generate`, `validate`, `rank`, `execute`, `schema`, `mongodb`, `history`, `chat`

```mermaid
flowchart LR
  A[User Prompt] --> B(Chat UI)
  B --> C[/POST /chat/]
  C --> D[NLU]
  C --> E[Generate]
  C --> F[Validate]
  C --> G[Rank]
  C --> H[Execute]
  H --> I[(DB)]
  H --> J[Results]
  J --> B
```

## 🧰 Tech Stack
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009485?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-06B6D4?logo=tailwindcss&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)
- Frontend: React, TypeScript, Vite, TailwindCSS, lucide-react
- Backend: FastAPI, Uvicorn, Pydantic, SQLAlchemy, PyMySQL, PyMongo
- Optional: spaCy (NLU), sentence-transformers/transformers (depending on generator)

## ✅ Prerequisites
- Node.js 18+
- Python 3.10+
- A MySQL database (for SQL features)
- Optionally MongoDB (for Mongo routes)

## ⚙️ Backend Setup
<details>
<summary><b>Show steps</b></summary>

```bash
cd backend
python -m venv .venv
\\.venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` and set at least:
```
DB_TYPE=mysql
DB_URI=mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME

# Optional generator settings
GENERATOR_PROVIDER=mixtral
GENERATOR_N_CANDIDATES=5
GENERATOR_TEMPERATURE=0.2
GENERATOR_TOP_P=0.95
GENERATOR_MAX_TOKENS=200

# For Mongo features
# MONGO_URI=mongodb://user:pass@host:27017
```

Run the API:
```bash
uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

</details>

## 💻 Frontend Setup
<details>
<summary><b>Show steps</b></summary>

```bash
cd project
npm install
```

Configure API base (optional). Create `project/.env`:
```
VITE_API_BASE=http://127.0.0.1:8000
```

Run the dev server:
```bash
npm run dev
```

Open the app and navigate to `http://localhost:5173/chatbot` (or your Vite dev URL).

</details>

## 🔌 Key Endpoints (Backend)
- `POST /chat/` — Unified chat: intent → generate → validate → rank → execute
- `POST /schema/inspect` — Inspect MySQL schema (or MongoDB via env)
- `POST /nlu/parse` — Intent + entities + dependencies
- `POST /generate/` — Generate SQL candidates
- `POST /validate/` — Validate SQL candidates
- `POST /rank/` — Rank SQL candidates
- `POST /execute/` — Execute SQL
- `POST /mongodb/*` — MongoDB NLU, generate, validate, execute
- `GET /history/*` — Query history ops

## 📚 API Documentation
- Open Swagger UI at: `http://127.0.0.1:8000/docs`
- Open ReDoc at: `http://127.0.0.1:8000/redoc`

## 🧪 API Playground
Try these once the backend is running.

```bash
# 1) Inspect schema
curl -s -X POST http://127.0.0.1:8000/schema/inspect -H "Content-Type: application/json" -d "{}" | jq

# 2) Ask a question via Chat API
curl -s -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" \
  -d '{
    "text": "Show last 10 customers by signup date",
    "db_type": "mysql"
  }' | jq

# 3) Direct SQL execution (advanced)
curl -s -X POST http://127.0.0.1:8000/execute -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM customers LIMIT 5",
    "db_type": "mysql"
  }' | jq
```

## 🤖 Using the Chatbot
1. Ensure backend is running and `DB_URI` is valid.
2. Open the Chatbot page.
3. Ask questions like:
   - "Show last 10 customers by signup date"
   - "Total revenue per month in 2024"
4. The bot will reply with detected intent, best SQL, and a summary of results.

### Sample Prompts
- "Top 5 products by sales in Q2"
- "List customers who placed more than 3 orders in the last 30 days"
- "Average order amount per customer"

### Tips
- Be specific about time ranges and sorting. Example: "last 30 days", "order by created_at desc".
- If you see no results, try a simpler version first.

## 🛠️ Troubleshooting
- **Bot stuck on “Thinking…”**
  - Verify backend logs. Confirm `VITE_API_BASE` points to the API URL.
  - Check CORS and that the backend is reachable at `http://127.0.0.1:8000`.
- **`DB_URI not set`**
  - Add `DB_URI` to `backend/.env` and restart Uvicorn.
- **No rows returned / errors**
  - Validate schema is correct; try simpler queries.
- **Generator configuration**
  - If using an external LLM provider in `core.generator`, ensure required API keys are configured.
 - **MongoDB features**
   - Ensure `MONGO_URI` is set and use the `/mongodb/*` endpoints.

## 👩‍💻 Development
- Frontend code: `project/src/`
- Backend routers: `backend/fastapi_app/routers/`
- Start backend and frontend in separate terminals for live reload.

## 🤝 Contributing
1. Create a feature branch.
2. Commit with clear messages.
3. Open a PR describing changes and testing steps.

## 📜 License
This repository may include third-party dependencies with their own licenses. Add a LICENSE file if you plan to open-source under a specific license.
