```markdown
# Downdetector API

A FastAPI-based web scraper that extracts outage and service status data from Downdetector websites.

## Features

- 🚀 Real-time scraping of Downdetector status pages  
- 📊 Time series data for service outages  
- 📈 Problem statistics and reports  
- 🌐 Multi-domain support (com.br, com, etc.)  
- ⏱️ Performance metrics included in responses  
- 🏢 Company directory listing  

## API Endpoints

### Get Service Status
`GET /status?company={company_name}&domain={domain}&timezone={timezone}`

**Parameters:**  
- `company` - Company name as it appears in Downdetector URL (required)  
- `domain` - Downdetector domain (default: "com.br")  
- `timezone` - Timezone for timestamps (default: "America/Maceio")  

### Get Company List
`GET /companylist?domain={domain}`

**Parameters:**  
- `domain` - Downdetector domain (default: "com.br")  

## Example Responses

### Service Status Response
```json
{
  "time_series": [
    {
      "date": "2023-10-15 14:00:00",
      "reports_value": 42,
      "baseline_value": 12
    }
  ],
  "most_reported_problems": [
    {
      "name": "Server connection",
      "percentage": "42%"
    }
  ],
  "stats": {
    "max_reports": {
      "value": 120,
      "timestamp": "2023-10-15 15:30:00"
    },
    "average_reports": 45.67,
    "total_reports": 1096,
    "max_deviation": {
      "value": 108,
      "timestamp": "2023-10-15 15:30:00"
    },
    "spikes": ["2023-10-15 15:30:00"],
    "alerts_count": 8
  },
  "duration_seconds": 3.456
}
```

### Company List Response
```json
{
  "companies": [
    {
      "full_company_link": "https://downdetector.com.br/status/pix/",
      "company_name": "PIX",
      "logo_url": "https://downdetector.com.br/logo/pix.png",
      "svg_data": {
        "data_values": "[1,2,3...]",
        "last_status": "up",
        "sparkline_color": "#00ff00"
      }
    }
  ],
  "duration_seconds": 5.123
}
```

## Installation

### Docker (Recommended)
```bash
docker-compose up -d
```

### Manual Installation
1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

2. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Configuration

**Environment variables:**
- `PYTHONUNBUFFERED=1` - Enable unbuffered logging  
- `PYTHONDONTWRITEBYTECODE=1` - Disable .pyc files  

## Technical Stack

- **Backend**: FastAPI + Uvicorn  
- **Scraping**: Playwright (Chromium)  
- **HTML Parsing**: BeautifulSoup4  
- **Time Handling**: pytz + python-dateutil  
- **Docker**: Pre-configured with all dependencies  

## License

MIT License
```

Key improvements made:
1. Proper Markdown formatting for code blocks with language specification
2. Consistent spacing between sections
3. Better parameter formatting in API documentation
4. Clearer section headers
5. Proper list formatting
6. Removed redundant backticks in endpoint documentation
7. Improved JSON example formatting

The file is now ready to be saved as `README.md` in your project root directory. It will render perfectly on GitHub with all the proper formatting.
