# 📡 Downdetector API

A **FastAPI-based web scraper** that extracts outage and service status data from Downdetector websites, with a modern dashboard interface.

---

## 🌟 Features

- **Real-time scraping** of Downdetector status pages
- **Time series data** for service outages and performance trends
- **Problem statistics** and detailed outage reports
- **Multi-domain support** (`.com.br`, `.com`, `.co.uk`, etc.)
- **Performance metrics** included in API responses
- **Company directory** with logos and sparkline visualizations
- **Modern dashboard** with dark/light mode and real-time updates
- **Docker-ready** with Nginx reverse proxy and caching
- **Automatic refresh** (10-minute intervals) with manual override
- **Search functionality** to filter companies by name
- **Status-based sorting** (outages → issues → operational)

---

## 🚀 Quick Start

### 🐳 Docker (Recommended)

1. **Clone and deploy:**
   ```bash
   docker-compose up -d
   ```

2. **Access the dashboard:**
   - **Dashboard:** http://localhost:8089
   - **API Documentation:** http://localhost:8089/docs (via FastAPI auto-docs)

### 💻 Manual Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Access directly:**
   - **API Server:** http://localhost:8000
   - **API Docs:** http://localhost:8000/docs
   - **OpenAPI Schema:** http://localhost:8000/openapi.json

---

## 📊 Dashboard Features

The included dashboard (`index.html`) provides:

- **Responsive grid layout** (2 to 10 columns based on screen size)
- **Real-time status indicators** with color coding:
  - 🟢 **Green**: Operational (`success`)
  - 🟡 **Yellow**: Issues detected (`warning`)
  - 🔴 **Red**: Service down (`danger`)
  - ⚫ **Gray**: Unknown/neutral status
- **Interactive cards** showing company logos and average report counts
- **Search bar** for quick company filtering
- **Theme toggle** (dark/light mode) with persistent preference
- **Auto-refresh countdown** (10 minutes) with manual refresh button
- **Collapsible navigation bar** for more screen space
- **Status summary** in footer showing operational/issue/down counts

---

## 📘 API Endpoints

### 🔎 Get Service Status
**GET** `/api/status?company={company_name}&domain={domain}&timezone={timezone}`

**Query Parameters:**
| Name       | Description                                                   | Default             | Required |
|------------|---------------------------------------------------------------|---------------------|----------|
| `company`  | Company name as it appears in the Downdetector URL           | –                   | Yes      |
| `domain`   | Downdetector domain (e.g., `com.br`, `com`, `co.uk`)         | `com.br`            | No       |
| `timezone` | Timezone for timestamps (TZ database name)                   | `America/Maceio`    | No       |

**Example:**
```bash
curl "http://localhost:8089/api/status?company=claro&domain=com.br"
```

---

### 🏢 Get Company List
**GET** `/api/companylist?domain={domain}`

**Query Parameters:**
| Name     | Description                  | Default   | Required |
|----------|------------------------------|-----------|----------|
| `domain` | Downdetector domain to query | `com.br`  | No       |

**Example:**
```bash
curl "http://localhost:8089/api/companylist"
```

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

### 🧾 Company List Response
```json
{
  "duration_seconds": 5.123,
  "companies": [
    {
      "full_company_link": "https://downdetector.com.br/status/pix/",
      "company_name": "PIX",
      "logo_url": "https://downdetector.com.br/logo/pix.png",
      "svg_data": {
        "data_values": "[1,2,3...]",
        "data_min": "0.0",
        "data_max": "42.0",
        "data_mean": 12.5,
        "data_stddev": 8.2,
        "last_status": "success",
        "sparkline_color": "rgb(22, 160, 176)",
        "sparkline_color_hex": "#16a0b0"
      }
    }
  ]
}
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Dashboard     │────▶│    Nginx     │────▶│   FastAPI       │
│   (Port 8089)   │     │  (Reverse    │     │   (Port 8000)   │
│                 │     │    Proxy)    │     │                 │
└─────────────────┘     └──────────────┘     └─────────┬───────┘
                                                        │
                                                ┌───────▼───────┐
                                                │   Playwright  │
                                                │   Scraper     │
                                                └───────────────┘
```

### Docker Services:
- **`downdetector`**: FastAPI + Playwright scraper
- **`nginx`**: Reverse proxy with caching and static file serving
- **Shared Network**: `app-network` for inter-container communication

---

## ⚙️ Configuration

### Nginx Settings (`nginx.conf`):
- **Port:** 80 (mapped to host port 8089)
- **Static file caching:** 1 year for assets
- **API response caching:** 10 seconds for 200/302 responses
- **CORS headers:** Enabled for all origins
- **Gzip compression:** Enabled for text-based content

### Environment Customization:
Modify `docker-compose.yml` to:
  - Change exposed ports
  - Adjust resource limits (CPU/memory)
  - Enable production deployment settings

### Dashboard Customization:
- Modify `index.html` for UI changes
- Update Tailwind config in `<script>` section for theme colors
- Adjust grid columns in `companiesGrid` CSS classes

---

## 🔧 Troubleshooting

### Common Issues:

1. **Playwright browser not installing:**
   ```bash
   # Inside container:
   docker exec -it downdetector playwright install
   ```

2. **Dashboard not loading companies:**
   - Check browser console for errors
   - Verify API is accessible: `curl http://localhost:8089/api/companylist`
   - Ensure containers are running: `docker ps`

3. **Slow API responses:**
   - Responses are cached for 10 seconds
   - Check `duration_seconds` in response for scraping time
   - Consider increasing `proxy_cache_valid` in nginx.conf

4. **Missing company logos:**
   - Some companies may not have logos on Downdetector
   - Fallback displays company name in text

---

## 📄 License & Attribution

- **Dashboard UI**: Custom built with Tailwind CSS and Material Icons
- **Data Source**: Downdetector (https://downdetector.com)
- **API Framework**: FastAPI (https://fastapi.tiangolo.com)
- **Browser Automation**: Playwright (https://playwright.dev)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📞 Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Open an issue in the repository

---

**Note**: This tool is for monitoring purposes only. Respect Downdetector's terms of service and implement appropriate rate limiting in production environments.

---

**Happy Monitoring!** 🚀
