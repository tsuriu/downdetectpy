from fastapi import FastAPI, Query
from typing import Optional
from .downdetector_scrapper import downdetector
from .downdetector_index import scrape_downdetector_links
import uvicorn
import time

app = FastAPI(title="Downdetector API")

@app.get("/status")
async def get_status(
    company: str = Query(..., description="Company name on Downdetector"),
    domain: str = Query("com.br", description="Downdetector domain (default: com.br)"),
    timezone: str = Query("America/Maceio", description="Timezone for timestamps (default: America/Maceio)")
):
    start_time = time.perf_counter()
    result = await downdetector(company, domain, timezone)
    end_time = time.perf_counter()

    duration = round(end_time - start_time, 3)  # Rounded to milliseconds
    if not result:
        return {"error": "Failed to retrieve data", "duration": duration}
    
    return {
        "duration_seconds": duration,
        **result
    }

@app.get("/companylist")
async def get_companiees(
    domain: str = Query("com.br", description="Downdetector domain (default: com.br)"),
):
    start_time = time.perf_counter()
    result = await scrape_downdetector_links(domain)
    end_time = time.perf_counter()

    duration = round(end_time - start_time, 3)  # Rounded to milliseconds
    if not result:
        return {"error": "Failed to retrieve data", "duration": duration}
    return {
        "duration_seconds": duration,
        **result
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)