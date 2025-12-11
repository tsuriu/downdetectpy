# 📡 Downdetector API

A **FastAPI-based web scraper** that extracts outage and service status data from Downdetector websites, with a modern dashboard interface.

---

## 🌟 Features

- **Intelligent caching system** - Limits requests to once every 10 minutes
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

## 🗄️ Cache Management Endpoints

The API includes an intelligent caching system that limits requests to Downdetector servers to once every 10 minutes. Subsequent requests return cached data.

### 📊 Cache Information
**GET** `/api/cache/info`
Returns detailed information about cached data including file sizes, expiration times, and cache statistics.

### 🗑️ Clear All Cache
**DELETE** `/api/cache/clear`
Clears all cached data, forcing the next request to fetch fresh data from Downdetector.

### ⏰ Clear Expired Cache
**DELETE** `/api/cache/clear/expired`
Clears only cache entries that have expired, keeping valid cached data.

---

## 📥 Example Responses

### ✅ Service Status Response (with cache metadata)
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
  "duration_seconds": 3.456,
  "company": "Claro",
  "domain": "com.br",
  "timezone": "America/Maceio",
  "cache_timestamp": "2023-12-11T10:30:00",
  "cache_expires_at": "2023-12-11T10:40:00",
  "from_cache": false,
  "cache_hit": false
}
```

---

### 🧾 Company List Response (with cache metadata)
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
  ],
  "domain": "com.br",
  "cache_timestamp": "2023-12-11T10:30:00",
  "cache_expires_at": "2023-12-11T10:40:00",
  "from_cache": true,
  "cache_hit": true
}
```

---

## 🏗️ Architecture

### Caching System Flow:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI   │────▶│   Cache     │────▶│  Downdetector│
│   Request   │     │   Endpoint  │     │   Layer     │     │   Scraper    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                        │                    │                    │
                        │   Cache Hit?       │   Cache Miss/Expired
                        │◀───────────────────│───────────────────▶│
                        │                    │                    │
                        │   Return Cached    │   Fetch New Data   │
                        │   Data (Instant)   │   (10+ seconds)    │
                        └───────────────────▶│◀───────────────────┘
```

### Docker Services:
- **`downdetector`**: FastAPI + Playwright scraper with caching layer
- **`nginx`**: Reverse proxy with additional caching and static file serving
- **Shared Network**: `app-network` for inter-container communication
- **Cache Directory**: `./cache` for persistent cache storage

---

## ⚙️ Configuration

### Cache Settings:
- **Cache Duration:** 10 minutes (600 seconds)
- **Cache Directory:** `./cache` (auto-created)
- **Cache File Format:** JSON with metadata
- **Auto-expiration:** Yes (based on timestamp)

### Nginx Settings (`nginx.conf`):
- **Port:** 80 (mapped to host port 8089)
- **Static file caching:** 1 year for assets
- **API response caching:** 10 seconds for 200/302 responses (additional layer)
- **CORS headers:** Enabled for all origins
- **Gzip compression:** Enabled for text-based content

### Environment Customization:
Modify `docker-compose.yml` to:
  - Change exposed ports
  - Adjust resource limits (CPU/memory)
  - Enable production deployment settings
  - Modify cache duration by setting environment variables

### Dashboard Customization:
- Modify `index.html` for UI changes
- Update Tailwind config in `<script>` section for theme colors
- Adjust grid columns in `companiesGrid` CSS classes
- Change auto-refresh interval in JavaScript (default: 10 minutes)

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
   - Check cache files: `ls -la ./cache/`

3. **Getting stale data:**
   - Cache automatically expires after 10 minutes
   - Manually clear cache: `curl -X DELETE http://localhost:8089/api/cache/clear`
   - Or clear only expired: `curl -X DELETE http://localhost:8089/api/cache/clear/expired`

4. **Cache not working:**
   - Ensure the `./cache` directory exists and is writable
   - Check permissions: `chmod 755 ./cache`
   - Verify cache info: `curl http://localhost:8089/api/cache/info`

5. **Slow first request, fast subsequent requests:**
   - This is expected behavior - first request scrapes Downdetector (slow)
   - Subsequent requests use cache (fast) until cache expires

6. **Missing company logos:**
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

**Note**: This tool is for monitoring purposes only. The built-in caching system helps respect Downdetector's servers by limiting requests to once every 10 minutes per endpoint. Implement additional rate limiting in production environments if needed.

---

**Happy Monitoring!** 🚀
