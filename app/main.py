import time

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .downdetector_index import scrape_downdetector_links
from .downdetector_scrapper import downdetector

app = FastAPI(title="Downdetector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/status")
async def get_status(
    company: str = Query(..., description="Company name on Downdetector"),
    domain: str = Query("com.br", description="Downdetector domain (default: com.br)"),
    timezone: str = Query(
        "America/Maceio",
        description="Timezone for timestamps (default: America/Maceio)",
    ),
):
    start_time = time.perf_counter()
    result = await downdetector(company, domain, timezone)
    end_time = time.perf_counter()

    duration = round(end_time - start_time, 3)  # Rounded to milliseconds

    if not result:
        return {"error": "Failed to retrieve data", "duration_seconds": duration}

    # Check if result is a dictionary before unpacking
    if isinstance(result, dict):
        return {"duration_seconds": duration, **result}
    else:
        # If result is a list or other type, wrap it appropriately
        return {"duration_seconds": duration, "data": result}


@app.get("/companylist")
async def get_companies(
    domain: str = Query("com.br", description="Downdetector domain (default: com.br)"),
):
    start_time = time.perf_counter()
    result = await scrape_downdetector_links(domain)
    end_time = time.perf_counter()

    duration = round(end_time - start_time, 3)

    if not result:
        return {"error": "Failed to retrieve data", "duration_seconds": duration}

    # Check if result is a dictionary before unpacking
    if isinstance(result, dict):
        return {"duration_seconds": duration, **result}
    else:
        # If result is a list or other type, wrap it appropriately
        return {"duration_seconds": duration, "companies": result}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
