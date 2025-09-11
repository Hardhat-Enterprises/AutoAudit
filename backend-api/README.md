# AutoAudit API

Automated GCP compliance assessment tool built with FastAPI. This API provides authentication and compliance assessment capabilities for GCP environments.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Hardhat-Enterprises/AutoAudit.git
   cd AutoAudit/backend-api
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**

   ```bash
   uv run uvicorn app.main:app --reload --port 3000
   ```

5. **Access the API**
   - API Documentation: http://localhost:3000/docs | http://localhost:3000/redoc
   - Root Endpoint: http://localhost:3000/

## 📁 Project Structure

```
backend-api/
├── app/
│   ├── api/
│   │   └── v1/               # Public + private endpoints
│   │
│   ├── core/                 # Config, logging, errors
│   │
│   ├── models/               # Pydantic DTOs
│   │
│   ├── services/             # Storage, CE adapter
│   │
│   └── main.py               # FastAPI app
│
├── tests/                    # Test scripts
│
├── .env.example              # Environment variables template
├── pyproject.toml            # Project dependencies & metadata
├── README.md
└── uv.lock                   # Lock file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b your-name/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`). Please follow [Conventional Commits](https://www.conventionalcommits.org)
4. Push to the branch (`git push origin your-name/amazing-feature`)
5. Open a Pull Request
