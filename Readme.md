---


# 📡 Downdetector API


A **FastAPI-based web scraper** that extracts outage and service status data from Downdetector websites.

---

## 🚀 Features

- Real-time scraping of Downdetector status pages  
- Time series data for service outages  
- Problem statistics and detailed reports  
- Multi-domain support (`.com.br`, `.com`, etc.)  
- Performance metrics included in responses  
- Company directory listing with logos and sparklines  

---

## 📘 API Endpoints

### 🔎 Get Service Status

GET /status?company={company_name}&domain={domain}&timezone={timezone}

**Query Parameters:**

| Name       | Description                                                   | Default             |
|------------|---------------------------------------------------------------|---------------------|
| `company`  | Company name as it appears in the Downdetector URL (required) | –                   |
| `domain`   | Downdetector domain                                           | `com.br`            |
| `timezone` | Timezone for timestamps (TZ string)                          | `America/Maceio`    |

---

### 🏢 Get Company List

GET /companylist?domain={domain}

**Query Parameters:**

| Name     | Description                  | Default   |
|----------|------------------------------|-----------|
| `domain` | Downdetector domain to query | `com.br`  |

---

## 📥 Example Responses

### ✅ Service Status Response

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

---

🧾 Company List Response

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

---

🛠️ Installation

🐳 Docker (Recommended)

`docker-compose up -d`

💻 Manual Setup
	1.	Install dependencies:

`pip install -r requirements.txt & playwright install`

  2. Run the FastAPI server:

`uvicorn app.main:app --host 0.0.0.0 --port 8000`

---
