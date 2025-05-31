# Downdetector API Scraper

A FastAPI-based service that scrapes Downdetector data for companies, providing time series reports, problem statistics, and summary metrics.

## Features

- 📊 Scrape Downdetector status pages for any company
- ⏳ Get 24-hour time series data (reports and baseline values)
- 🔍 Identify most reported problems with percentages
- 📈 Compute summary statistics
- 🌎 Support for multiple domains and timezones
- 🐳 Docker support for easy deployment

## Statistics Explained

The `stats` object contains these computed metrics:

| Key | Description | Type |
|------|-------------|------|
| `max_reports` | Peak report value and timestamp | Object |
| `average_reports` | Mean of all report values | Float |
| `total_reports` | Sum of all report values | Float |
| `max_deviation` | Largest difference between reports and baseline | Object |
| `spikes` | Timestamps where reports > 2× baseline | Array |
| `alerts_count` | Count of reports > 1.5× baseline | Integer |

## Installation

### Option 1: Local Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/downdetector-scraper.git
   cd downdetector-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

### Option 2: Docker Installation
1. Build the Docker image:
   ```bash
   docker build -t downdetector-scraper .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name downdetector downdetector-scraper
   ```

## Usage

### Running the API

**Local:**
```bash
python main.py
```

**Docker:**
```bash
docker start downdetector
```

The API will be available at `http://localhost:8000`

### API Endpoint

**GET /status**

Parameters:
- `company`: Company name (required)
- `domain`: Downdetector domain (default: "com.br")
- `timezone`: Timezone for timestamps (default: "America/Maceio")

Example request:
```bash
curl "http://localhost:8000/status?company=pix&domain=com.br&timezone=America/Sao_Paulo"
```

## Docker Compose

For production deployments, use `docker-compose.yml`:

```bash
docker-compose up -d
```
