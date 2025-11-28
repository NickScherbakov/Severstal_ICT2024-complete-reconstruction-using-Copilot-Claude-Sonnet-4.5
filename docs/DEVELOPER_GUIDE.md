# TITAN Analytics Platform - Developer Documentation

## Quick Start for Developers

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15 (or use Docker)

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/NickScherbakov/Severstal_ICT2024.git
cd Severstal_ICT2024

# Start infrastructure services
docker-compose -f docker-compose-dev.yml up -d

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend setup (new terminal)
cd titan_frontend
npm install
npm run dev
```

---

## Architecture Overview

### Backend Structure

```
backend/
├── accounts/           # Core data models & processors
│   ├── models.py       # Database models
│   ├── processors.py   # AI data processors
│   ├── handlers.py     # Data handlers
│   └── tasks.py        # Celery async tasks
├── analyst/            # Django project settings
│   ├── settings.py     # Configuration
│   ├── urls.py         # URL routing
│   └── celery.py       # Celery configuration
├── analytics/          # Analytics utilities
│   └── monitoring.py   # Monitoring & metrics
├── api/                # REST API
│   └── v1/             # API version 1
│       ├── views.py    # API views
│       ├── serializers.py
│       └── urls.py
├── export/             # Export functionality
│   ├── pdf.py          # PDF generation
│   ├── word.py         # Word document generation
│   └── excel.py        # Excel export
├── extract/            # Data extraction
│   ├── html.py         # HTML parsing
│   ├── pdf.py          # PDF parsing
│   └── reports.py      # Report extraction
├── search/             # Search engine
│   ├── search.py       # Search implementation
│   ├── yagpt.py        # YandexGPT integration
│   └── video.py        # Video search
└── users/              # User management
    ├── models.py       # User, Role, Organization
    └── permissions.py  # RBAC permissions
```

### Frontend Structure

```
titan_frontend/
├── src/
│   ├── api/            # API client
│   ├── components/     # React components
│   │   ├── ui/         # Base UI components
│   │   └── ...         # Feature components
│   ├── routes/         # Page routes
│   ├── services/       # Business logic
│   └── utils/          # Utilities
└── public/             # Static assets
```

---

## API Reference

### Authentication

```bash
# Get authentication token
POST /api/v1/auth/
Content-Type: application/json
{
  "username": "your_username",
  "password": "your_password"
}

# Response
{
  "token": "your_auth_token"
}

# Use token in requests
Authorization: Token your_auth_token
```

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/templates/` | List templates |
| POST | `/api/v1/templates/` | Create template |
| GET | `/api/v1/marketplace/` | Public templates |
| GET | `/api/v1/reports/` | List user reports |
| POST | `/api/v1/reports/` | Create report |
| GET | `/api/v1/search/?q=query` | Search data |
| GET | `/api/v1/processors/` | List processors |

### Health Endpoints

| Endpoint | Description |
|----------|-------------|
| `/health/` | Liveness probe |
| `/ready/` | Readiness probe |

---

## Creating Custom Processors

TITAN's modular architecture allows easy addition of custom data processors.

### Step 1: Create Processor Class

```python
# backend/accounts/custom_processors.py

from accounts.processors import (
    DataProcessor, 
    ProcessorRegistry, 
    ProcessorMetadata,
    LLMIntegration
)

class MyCustomProcessor(DataProcessor):
    """
    Custom processor for specialized analysis
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='MyCustomProcessor',
            description='Description of what this processor does',
            category='custom',
            supported_data_types=['text', 'json'],
            output_types=['json', 'visualization'],
            requires_llm=True,
            is_enterprise=False,
            version='1.0.0',
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'my_custom_type'
    
    def process(self, data: Any, params: Dict) -> Dict:
        # Extract text from data
        text = data.get('data') if isinstance(data, dict) else str(data)
        
        # Create prompt for LLM
        prompt = f"""Your analysis prompt here.
        
        Data: {text[:2000]}
        """
        
        # Get LLM response (multi-LLM support)
        provider = params.get('model', 'yandexgpt')
        result = LLMIntegration.get_llm_response(prompt, provider, params)
        
        # Parse and return result
        return {
            'type': 'my_custom_type',
            'result': result,
            'visualization': 'custom_chart'
        }
```

### Step 2: Register Processor

```python
# In accounts/processors.py, add to ProcessorRegistry.initialize():

cls.register(MyCustomProcessor())
```

### Step 3: Add Block Type

```python
# In accounts/models.py, add to MetaBlock:

MY_CUSTOM = 'my_custom_type'

TYPES = (
    # ... existing types
    (MY_CUSTOM, 'My Custom Analysis'),
)
```

---

## RBAC Permissions

### Available Permissions

| Permission | Description | Roles |
|------------|-------------|-------|
| `create_reports` | Create analytics reports | Admin, Analyst, Enterprise |
| `view_reports` | View reports | All |
| `delete_reports` | Delete reports | Admin, Analyst, Enterprise |
| `manage_templates` | Manage all templates | Admin |
| `create_templates` | Create new templates | Admin, Analyst, Enterprise |
| `publish_templates` | Publish to marketplace | Admin, Enterprise |
| `manage_users` | Manage user accounts | Admin |
| `api_access` | Access REST API | Admin, Analyst, Enterprise |
| `priority_processing` | Priority job queue | Enterprise |
| `advanced_analytics` | Advanced features | Enterprise |

### Using Permissions in Views

```python
from users.permissions import RBACPermission, require_permission

# DRF ViewSet
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [RBACPermission]
    required_permission = 'create_reports'

# Function-based view
@require_permission('create_reports')
def my_view(request):
    ...
```

---

## Multi-LLM Configuration

### Supported Providers

| Provider | Model IDs | Configuration |
|----------|-----------|---------------|
| YandexGPT | `yandexgpt`, `yandexgpt-lite` | `YANDEX_SEARCH_API_TOKEN` |
| OpenAI | `gpt-4`, `gpt-3.5-turbo` | `OPENAI_API_KEY` |
| Anthropic | `claude-3` | `ANTHROPIC_API_KEY` |

### Configuration

```python
# settings.py or environment variables
YANDEX_SEARCH_API_TOKEN = "your-yandex-token"
OPENAI_API_KEY = "your-openai-key"
ANTHROPIC_API_KEY = "your-anthropic-key"

# Default provider
DEFAULT_LLM_PROVIDER = "yandexgpt"
```

### Usage in Processors

```python
from accounts.processors import LLMIntegration

# Use default provider
result = LLMIntegration.get_llm_response("Your prompt")

# Specify provider
result = LLMIntegration.get_llm_response(
    "Your prompt",
    provider="gpt-4",
    params={"temperature": 0.7}
)
```

---

## Testing

### Running Tests

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd titan_frontend
npm run test
```

### Writing Tests

```python
# backend/tests/test_processors.py

from django.test import TestCase
from accounts.processors import ProcessorRegistry, SentimentAnalysisProcessor

class ProcessorTests(TestCase):
    def test_sentiment_processor_registration(self):
        processors = ProcessorRegistry.list_processors()
        self.assertIn('SentimentAnalysisProcessor', processors)
    
    def test_sentiment_can_process(self):
        processor = SentimentAnalysisProcessor()
        self.assertTrue(processor.can_process('sentiment'))
        self.assertFalse(processor.can_process('timeline'))
```

---

## Deployment

### Docker Deployment

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Scale workers
docker-compose up -d --scale celery=4
```

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f deploy/kubernetes/ -n titan

# Check status
kubectl get pods -n titan

# View logs
kubectl logs -f deployment/titan-backend -n titan
```

---

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run linting: `flake8 backend/` and `npm run lint`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push and create Pull Request

### Code Style

- Python: Follow PEP 8, use Black formatter
- TypeScript: Follow project ESLint configuration
- Documentation: Include docstrings for all public methods

---

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/NickScherbakov/Severstal_ICT2024/issues)
- **Documentation**: [Full documentation](https://nickscherbakov.github.io/Severstal_ICT2024/)
