# ZZP Scanner - Self-Employed Business Website Detector

Een geavanceerd systeem dat automatisch zelfstandige ondernemers (ZZP'ers) en kleine bedrijven identificeert die geen eigen website hebben binnen Nederland, België, Luxemburg en Duitsland.

## 🎯 Doelstelling

Het systeem combineert data crawling, website verificatie en intelligente data verwerking om een complete database op te bouwen van potentiële klanten voor webontwikkeling diensten.

## 🏗️ Architectuur

Het systeem is gebouwd met een moderne microservice-architectuur:

- **FastAPI**: Moderne Python web framework voor de API
- **PostgreSQL**: Primaire database voor business data
- **Redis**: Caching en message queue
- **Celery**: Asynchrone task processing
- **Elasticsearch**: Zoekfunctionaliteit
- **Docker**: Containerisatie voor eenvoudige deployment

## 🚀 Quick Start

### Vereisten

- Docker en Docker Compose
- Python 3.11+
- Minimaal 4GB RAM beschikbaar

### Installatie

1. **Clone het project:**
```bash
git clone <repository-url>
cd scanner
```

2. **Start de services:**
```bash
docker-compose up -d
```

3. **Wacht tot alle services gestart zijn:**
```bash
docker-compose logs -f
```

4. **Open de applicatie:**
- API Documentation: http://localhost:8000/docs
- Dashboard: http://localhost:8000
- Flower (Celery monitoring): http://localhost:5555

## 📊 Functionaliteiten

### Core Features

- **Automatische Data Crawling**: Scraping van Google Maps, LinkedIn, en andere bronnen
- **Website Verificatie**: DNS lookup, Google Search, WHOIS checks
- **Business Classification**: Automatische identificatie van ZZP'ers
- **Data Export**: CSV en Excel export functionaliteit
- **Real-time Monitoring**: Dashboard met statistieken en monitoring

### API Endpoints

#### Businesses
- `GET /api/v1/businesses/` - Lijst van bedrijven
- `GET /api/v1/businesses/{id}` - Specifiek bedrijf
- `POST /api/v1/businesses/` - Nieuw bedrijf toevoegen
- `GET /api/v1/businesses/stats/summary` - Statistieken
- `GET /api/v1/businesses/search/` - Zoeken

#### Jobs
- `GET /api/v1/jobs/` - Lijst van crawl jobs
- `POST /api/v1/jobs/start-google-maps-crawl` - Start Google Maps crawl
- `POST /api/v1/jobs/start-website-check` - Start website verificatie

#### Exports
- `POST /api/v1/exports/businesses/csv` - Export naar CSV
- `POST /api/v1/exports/businesses/excel` - Export naar Excel
- `GET /api/v1/exports/zzp-without-website` - ZZP zonder website

#### Dashboard
- `GET /api/v1/dashboard/stats` - Dashboard statistieken
- `GET /api/v1/dashboard/recent-activity` - Recente activiteit
- `GET /api/v1/dashboard/top-cities` - Top steden
- `GET /api/v1/dashboard/top-industries` - Top industrieën

## 🔧 Configuratie

### Environment Variables

Maak een `.env` bestand aan in de root directory:

```env
# Database
DATABASE_URL=postgresql://scanner:scanner123@localhost:5432/scanner

# Redis
REDIS_URL=redis://localhost:6379

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# API Keys (optioneel)
GOOGLE_API_KEY=your_google_api_key
LINKEDIN_API_KEY=your_linkedin_api_key
FACEBOOK_API_KEY=your_facebook_api_key

# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Crawling Settings
CRAWL_DELAY=1.0
MAX_CONCURRENT_REQUESTS=16
REQUEST_TIMEOUT=30

# Export Settings
EXPORT_DIR=/app/exports
MAX_EXPORT_SIZE=10000
```

### Docker Services

Het systeem bestaat uit de volgende services:

- **app**: Hoofdapplicatie (FastAPI)
- **postgres**: PostgreSQL database
- **redis**: Redis cache en message queue
- **elasticsearch**: Elasticsearch zoekengine
- **celery_worker**: Celery worker voor background tasks
- **celery_beat**: Celery scheduler
- **flower**: Celery monitoring
- **nginx**: Reverse proxy

## 📈 Gebruik

### 1. Start een Crawl Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/start-google-maps-crawl" \
  -H "Content-Type: application/json" \
  -d '{"location": "Amsterdam, Netherlands", "industry": "webdesign"}'
```

### 2. Check Website Status

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/start-website-check" \
  -H "Content-Type: application/json" \
  -d '{"business_ids": [1, 2, 3]}'
```

### 3. Export Data

```bash
# Export alle bedrijven naar CSV
curl -X POST "http://localhost:8000/api/v1/exports/businesses/csv" \
  -H "Content-Type: application/json" \
  -d '{"city": "Amsterdam", "website_exists": false}'

# Export ZZP zonder website
curl -X GET "http://localhost:8000/api/v1/exports/zzp-without-website"
```

### 4. Bekijk Statistieken

```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/stats"
```

## 🔍 Monitoring

### Flower Dashboard
- URL: http://localhost:5555
- Monitor Celery tasks en workers
- Bekijk task queues en performance

### API Documentation
- URL: http://localhost:8000/docs
- Interactieve API documentatie
- Test endpoints direct

### Logs
```bash
# Bekijk applicatie logs
docker-compose logs -f app

# Bekijk Celery worker logs
docker-compose logs -f celery_worker

# Bekijk database logs
docker-compose logs -f postgres
```

## 🛠️ Development

### Local Development Setup

1. **Clone en setup:**
```bash
git clone <repository-url>
cd scanner
python -m venv venv
source venv/bin/activate  # Linux/Mac
# of
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

2. **Database setup:**
```bash
docker-compose up -d postgres redis elasticsearch
alembic upgrade head
```

3. **Run development server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_businesses.py
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/
```

## 📁 Project Structuur

```
scanner/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── businesses.py
│   │   │   ├── jobs.py
│   │   │   ├── exports.py
│   │   │   ├── dashboard.py
│   │   │   └── website_checks.py
│   │   └── routes.py
│   ├── config/
│   │   └── settings.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── business.py
│   │   ├── crawl_job.py
│   │   └── website_check.py
│   ├── schemas/
│   │   └── business.py
│   ├── services/
│   │   └── celery_app.py
│   └── main.py
├── data/
├── docs/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔒 Security

- Alle API endpoints zijn beveiligd
- Rate limiting is geïmplementeerd
- Input validatie met Pydantic
- SQL injection protection via SQLAlchemy
- CORS configuratie voor web clients

## 🚀 Deployment

### Production Deployment

1. **Environment setup:**
```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=false
export SECRET_KEY=your-secure-secret-key
```

2. **Database migrations:**
```bash
alembic upgrade head
```

3. **Start services:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

## 🤝 Bijdragen

1. Fork het project
2. Maak een feature branch (`git checkout -b feature/amazing-feature`)
3. Commit je wijzigingen (`git commit -m 'Add amazing feature'`)
4. Push naar de branch (`git push origin feature/amazing-feature`)
5. Open een Pull Request

## 📄 Licentie

Dit project is gelicenseerd onder de MIT License - zie het [LICENSE](LICENSE) bestand voor details.

## 📞 Support

Voor vragen of ondersteuning:

- Open een issue op GitHub
- Neem contact op via email
- Bekijk de documentatie in `/docs`

## 🔄 Roadmap

### Fase 1: MVP (4-6 weken) ✅
- [x] Basis Scrapy spiders voor Google Maps
- [x] Eenvoudige website checker
- [x] PostgreSQL database setup
- [x] Basis FastAPI
- [x] Eenvoudig dashboard
- [x] CSV export functionaliteit

### Fase 2: Uitbreiding (6-8 weken)
- [ ] LinkedIn API integratie
- [ ] Geavanceerde website verificatie
- [ ] Data enrichment pipeline
- [ ] Elasticsearch integratie
- [ ] Verbeterd dashboard
- [ ] API rate limiting

### Fase 3: Productie (4-6 weken)
- [ ] Docker containerisatie
- [ ] Kubernetes deployment
- [ ] Monitoring en logging
- [ ] Performance optimalisatie
- [ ] Security hardening
- [ ] Backup strategie

### Fase 4: Schaalvergroting (Ongoing)
- [ ] Machine learning classificatie
- [ ] Real-time data processing
- [ ] Multi-region support
- [ ] Advanced analytics
- [ ] Mobile app

---

**ZZP Scanner** - Automatische identificatie van zelfstandige ondernemers zonder website 