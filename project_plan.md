# Technisch Aanpakplan: ZZP Scanner Systeem

## 1. Inleiding

Dit systeem is ontworpen om automatisch zelfstandige ondernemers (ZZP'ers) en kleine bedrijven te identificeren die geen eigen website hebben binnen Nederland, België, Luxemburg en Duitsland. Het systeem combineert data crawling, website verificatie en intelligente data verwerking om een complete database op te bouwen van potentiële klanten voor webontwikkeling diensten.

### Doelstellingen
- Automatische identificatie van ZZP'ers zonder website
- Schaalbare architectuur voor grote datasets
- Betrouwbare website verificatie
- Export functionaliteit voor sales teams
- Toekomstbestendige en onderhoudbare codebase

## 2. Globale Architectuur

```mermaid
graph TB
    subgraph "Data Sources"
        A[Google Maps API]
        B[LinkedIn API]
        C[Facebook Graph API]
        D[Chamber of Commerce APIs]
        E[Local Business Directories]
    end
    
    subgraph "Crawling Layer"
        F[Scrapy Spiders]
        G[API Connectors]
        H[Rate Limiter]
    end
    
    subgraph "Processing Layer"
        I[Data Validator]
        J[Business Classifier]
        K[Website Checker]
        L[Data Enricher]
    end
    
    subgraph "Storage Layer"
        M[PostgreSQL]
        N[Redis Cache]
        O[Elasticsearch]
    end
    
    subgraph "Application Layer"
        P[Flask API]
        Q[Dashboard]
        R[Export Service]
        S[Task Scheduler]
    end
    
    A --> F
    B --> G
    C --> G
    D --> G
    E --> F
    
    F --> I
    G --> I
    
    I --> J
    J --> K
    K --> L
    
    L --> M
    L --> N
    L --> O
    
    M --> P
    N --> P
    O --> P
    
    P --> Q
    P --> R
    P --> S
```

## 3. Modules

### 3.1 Crawling Module

**Functionaliteit:**
- Automatische data extractie uit diverse bronnen
- Rate limiting en respect voor robots.txt
- Duplicate detection
- Geografische filtering (Benelux + Duitsland)

**Tech Stack:**
- **Scrapy 2.11+**: Hoofd framework voor web scraping
- **Selenium**: Voor JavaScript-heavy sites
- **Requests**: Voor API calls
- **BeautifulSoup4**: HTML parsing
- **GeoPy**: Geografische validatie
- **Celery**: Asynchrone task processing

**Implementatie:**
```python
# Voorbeeld spider structuur
class BusinessSpider(scrapy.Spider):
    name = 'business_spider'
    
    def parse(self, response):
        # Extract business data
        # Validate location
        # Store in pipeline
```

### 3.2 Website Checker Module

**Functionaliteit:**
- DNS lookup verificatie
- Google Search API integratie
- WHOIS data extractie
- Website availability check
- SSL certificaat validatie

**Tech Stack:**
- **dnspython**: DNS resolutie
- **whois**: WHOIS data extractie
- **requests**: HTTP status checks
- **Google Search API**: Web presence verificatie
- **ssl**: SSL certificaat validatie

**Implementatie:**
```python
class WebsiteChecker:
    def check_website_exists(self, business_name, location):
        # Google Search
        # DNS Lookup
        # WHOIS Check
        # Return confidence score
```

### 3.3 Data Verwerking en Opslag Module

**Functionaliteit:**
- Data normalisatie en cleaning
- Business classification (ZZP vs. groot bedrijf)
- Duplicate detection en merging
- Data enrichment
- Export functionaliteit

**Tech Stack:**
- **PostgreSQL 15+**: Primaire database
- **Redis**: Caching en session storage
- **Elasticsearch**: Zoekfunctionaliteit
- **Pandas**: Data processing
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations

**Database Schema:**
```sql
-- Businesses table
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(255),
    business_type VARCHAR(100),
    website_exists BOOLEAN DEFAULT FALSE,
    website_url VARCHAR(500),
    confidence_score DECIMAL(3,2),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes voor performance
CREATE INDEX idx_businesses_location ON businesses(city, country);
CREATE INDEX idx_businesses_website ON businesses(website_exists);
CREATE INDEX idx_businesses_confidence ON businesses(confidence_score);
```

### 3.4 Dashboard/Export Module

**Functionaliteit:**
- Web dashboard voor data visualisatie
- Export naar CSV/Excel
- API endpoints voor integratie
- Real-time monitoring
- Filtering en zoekfunctionaliteit

**Tech Stack:**
- **Flask 3.0+**: Web framework
- **React**: Frontend dashboard
- **Chart.js**: Data visualisatie
- **Bootstrap**: UI framework
- **JWT**: Authentication
- **Swagger**: API documentatie

## 4. Tech Stack Samenvatting

### Backend
- **Python 3.11+**: Hoofdprogrammeertaal
- **FastAPI**: Moderne API framework
- **PostgreSQL**: Primaire database
- **Redis**: Caching en queues
- **Celery**: Task scheduling
- **Docker**: Containerisatie

### Data Processing
- **Pandas**: Data manipulation
- **NumPy**: Numerieke berekeningen
- **Scikit-learn**: Machine learning (toekomstig)
- **Elasticsearch**: Zoekengine

### Crawling & APIs
- **Scrapy**: Web scraping
- **Selenium**: Browser automation
- **Requests**: HTTP client
- **Google APIs**: Search en Maps
- **LinkedIn API**: Business data

### Infrastructure
- **Docker Compose**: Local development
- **Kubernetes**: Production deployment
- **Nginx**: Reverse proxy
- **Prometheus**: Monitoring
- **Grafana**: Visualisatie

## 5. Roadmap / MVP Voorstel

### Fase 1: MVP (4-6 weken)
- [ ] Basis Scrapy spiders voor Google Maps
- [ ] Eenvoudige website checker
- [ ] PostgreSQL database setup
- [ ] Basis Flask API
- [ ] Eenvoudig dashboard
- [ ] CSV export functionaliteit

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

## 6. Toekomstige Uitbreidingen

### Machine Learning Integratie
- **Scikit-learn**: Business classification
- **TensorFlow**: Website quality scoring
- **NLTK**: Text analysis van business descriptions

### Advanced Analytics
- **Apache Kafka**: Real-time data streaming
- **Apache Spark**: Big data processing
- **Jupyter Notebooks**: Data analysis

### API Integraties
- **Chamber of Commerce APIs**: Officiële business data
- **Social Media APIs**: Instagram, Twitter
- **Local Business Directories**: Yellow Pages, etc.

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Dashboarding
- **ELK Stack**: Logging
- **Sentry**: Error tracking

## 7. Implementatie Details

### Project Structuur
```
scanner/
├── app/
│   ├── api/
│   ├── crawlers/
│   ├── models/
│   ├── services/
│   └── utils/
├── config/
├── data/
├── docs/
├── tests/
├── docker/
└── requirements.txt
```

### Environment Setup
```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# of
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Database setup
docker-compose up -d postgres redis
alembic upgrade head

# Run development server
python app/main.py
```

### Docker Compose Setup
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: scanner
      POSTGRES_USER: scanner
      POSTGRES_PASSWORD: scanner123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - elasticsearch
    environment:
      DATABASE_URL: postgresql://scanner:scanner123@postgres:5432/scanner
      REDIS_URL: redis://redis:6379
      ELASTICSEARCH_URL: http://elasticsearch:9200

volumes:
  postgres_data:
```

Dit plan biedt een solide basis voor een schaalbaar en onderhoudbaar systeem dat automatisch ZZP'ers zonder website kan identificeren in de Benelux en Duitsland. 