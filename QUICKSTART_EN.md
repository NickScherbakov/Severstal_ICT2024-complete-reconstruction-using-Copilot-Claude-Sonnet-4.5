# 🎯 TITAN Analytics Platform - Quick Start

**Get started in 5 minutes with examples!**

---

## 🚀 Launch (choose one method)

### Option 1: Docker (recommended)

```bash
git clone https://github.com/allseeteam/Severstal_ICT2024.git
cd Severstal_ICT2024
cp .env.example .env

docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py load_template_library

# Done! Open http://localhost:8000
```

### Option 2: Local

```bash
git clone https://github.com/allseeteam/Severstal_ICT2024.git
cd Severstal_ICT2024/backend

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
docker-compose -f docker-compose-dev.yml up -d  # DB and RabbitMQ

python manage.py migrate
python manage.py createsuperuser
python manage.py load_template_library

python manage.py runserver
# Open http://localhost:8000
```

---

## 📚 First Steps

### 1️⃣ Explore the Marketplace

```bash
curl http://localhost:8000/api/v1/marketplace/
```

Or open in browser: http://localhost:8000/api/v1/swagger/

### 2️⃣ Get authorization token

```bash
curl -X POST http://localhost:8000/api/v1/auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

Save the token:
```json
{"token":"a1b2c3d4e5f6..."}
```

### 3️⃣ Create your first report

```bash
TOKEN="your_token"

# List templates
curl http://localhost:8000/api/v1/template/ \
  -H "Authorization: Token $TOKEN"

# Create report
curl -X POST http://localhost:8000/api/v1/report/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template": 1,
    "search_query_text": "artificial intelligence",
    "search_start": "2024-01-01",
    "search_end": "2024-12-31"
  }'
```

---

## 💡 Usage Examples

### Example 1: Market Analysis

```python
import requests

# Authentication
response = requests.post(
    'http://localhost:8000/api/v1/auth/',
    json={'username': 'admin', 'password': 'password'}
)
token = response.json()['token']
headers = {'Authorization': f'Token {token}'}

# Find "Market Analysis" template
templates = requests.get(
    'http://localhost:8000/api/v1/marketplace/',
    params={'search': 'market analysis'}
).json()

template_id = templates['results'][0]['id']

# Create report
report = requests.post(
    'http://localhost:8000/api/v1/report/',
    json={
        'template': template_id,
        'search_query_text': 'AI technology market 2024',
        'search_start': '2024-01-01',
        'search_end': '2024-10-01'
    },
    headers=headers
).json()

print(f"Report created: {report['id']}")
```

### Example 2: Creating a Custom Template

```python
from accounts.models import *

# Theme
theme = Theme.objects.create(name="Competitive Analysis")

# Category
category = TemplateCategory.objects.get(slug='business')

# Template
template = Template.objects.create(
    name="Competitor Monitoring",
    description="Track competitor activities",
    theme=theme,
    category=category,
    tags=['competitors', 'monitoring'],
    is_public=True
)

# Blocks
blocks = [
    ("List of competitors {theme}", "table", 0),
    ("Sentiment analysis of mentions {theme}", "sentiment", 1),
    ("Dynamic trend chart {theme}", "plotly", 2),
    ("Action forecast {theme}", "forecast", 3),
]

for query, block_type, pos in blocks:
    MetaBlock.objects.create(
        query_template=query,
        template=template,
        type=block_type,
        position=pos
    )

print(f"✅ Template ready! ID: {template.id}")
```

### Example 3: Using Processors

```python
from accounts.processors import ProcessorRegistry

# Sentiment analysis
sentiment_processor = ProcessorRegistry.get_processor('sentiment')
result = sentiment_processor.process(
    data={'data': 'Great product, highly recommend to everyone!'},
    params={'model': 'yandexgpt'}
)
print(result)

# Network graph
network_processor = ProcessorRegistry.get_processor('network')
result = network_processor.process(
    data={'data': 'Apple acquired startup Acme. CEO John Smith became VP.'},
    params={}
)
print(result['graph_data'])
```

### Example 4: Template Export/Import

```python
import json
import requests

# Export
export = requests.post(
    f'http://localhost:8000/api/v1/templates-extended/1/export/',
    headers=headers
).json()

# Save to file
with open('my_template.json', 'w', encoding='utf-8') as f:
    json.dump(export, f, ensure_ascii=False, indent=2)

# Import on another server
with open('my_template.json', 'r', encoding='utf-8') as f:
    template_data = json.load(f)

imported = requests.post(
    'http://another-server.com/api/v1/templates-extended/import/',
    json=template_data,
    headers=headers
).json()

print(f"Imported: {imported['id']}")
```

---

## 🎨 Available Block Types

| Type | Description | Usage Example |
|-----|----------|---------------------|
| `plotly` | Charts | Price dynamics, volumes |
| `text` | Text | Descriptions, conclusions |
| `video` | Video | YouTube reviews |
| `table` | Table | Lists, comparisons |
| `map` | Map | Geographic data |
| `timeline` | Timeline | Event chronology |
| `network` | Graph | Company relationships |
| `comparison` | Comparison | SWOT, competitors |
| `sentiment` | Sentiment | Review analysis |
| `forecast` | Forecast | Trend predictions |

---

## 📊 Ready-Made Templates

After running `load_template_library`, available templates:

### 💼 Business
- **Comprehensive Market Analysis** - volume, players, trends, SWOT
- **Competitive Intelligence** - comparison, strategies, forecasts

### 🔬 Science
- **Systematic Literature Review** - publications, citations, trends

### 📺 Media
- **Brand Reputation Monitoring** - mentions, sentiment, dynamics

### ⚖️ Legal
- **Legislative Monitoring** - changes, impact, recommendations

### 🎓 Education
- **Comprehensive Topic Study** - theory, concepts, examples

---

## 🛠 Useful Commands

```bash
# View all templates
python manage.py shell
>>> from accounts.models import Template
>>> for t in Template.objects.all(): print(t.id, t.name)

# Export data
python manage.py model2csv accounts.Template > templates.csv

# Generate search index
python generate_search.py search.pkl

# Run Celery worker
celery -A analyst worker -l info

# View processors
python manage.py shell
>>> from accounts.processors import ProcessorRegistry
>>> ProcessorRegistry.list_processors()
```

---

## 📖 Documentation

- **Full documentation**: [README.md](./README.md)
- **API Reference**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)
- **Upgrade Guide**: [UPGRADE_GUIDE.md](./UPGRADE_GUIDE.md)
- **Swagger UI**: http://localhost:8000/api/v1/swagger/

---

## 🎯 Next Steps

1. ✅ Explore ready-made templates in Marketplace
2. ✅ Create your first report
3. ✅ Configure favorite templates
4. ✅ Experiment with processors
5. ✅ Create a custom template for your tasks
6. ✅ Share your results in Issues!

---

## ❓ FAQ

**Q: Where to find API token?**  
A: `POST /api/v1/auth/` with username/password

**Q: How to add a new processing type?**  
A: Create a class inheriting from `DataProcessor` and register via `ProcessorRegistry.register()`

**Q: Can I use it without YandexGPT?**  
A: Yes, but some processors (sentiment, network) require an AI model

**Q: How to export a report?**  
A: `POST /api/v1/report/{id}/download_report/` with parameter `type=pdf|msword|excel`

**Q: Are there limits on number of templates?**  
A: No, create as many as you need!

---

## 🆘 Help

- 📝 [GitHub Issues](https://github.com/allseeteam/Severstal_ICT2024/issues)
- 💬 [Discussions](https://github.com/allseeteam/Severstal_ICT2024/discussions)
- 📚 [Full Documentation](./README.md)

---

**Ready for analytics? Let's go!** 🚀🎯

⭐ Don't forget to star the project on GitHub!
