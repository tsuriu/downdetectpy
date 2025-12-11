import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .downdetector_index import scrape_downdetector_links
from .downdetector_scrapper import downdetector

app = FastAPI(title="Downdetector API")

# Cache configuration
CACHE_DIR = "./cache"
COMPANY_CACHE_FILE = os.path.join(CACHE_DIR, "companylist_cache.json")
CACHE_DURATION = 10 * 60  # 10 minutes in seconds

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


def ensure_cache_dir():
    """Ensure cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def load_cached_data(cache_file: str) -> Optional[Dict[str, Any]]:
    """Load cached data if it exists and is still valid."""
    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if cache is still valid
        cache_timestamp = datetime.fromisoformat(data.get("cache_timestamp", ""))
        current_time = datetime.now()

        if current_time - cache_timestamp < timedelta(seconds=CACHE_DURATION):
            return data
        else:
            # Cache expired
            os.remove(cache_file)  # Remove expired cache
            return None
    except (json.JSONDecodeError, ValueError, KeyError, FileNotFoundError):
        # If there's any error reading the cache, remove it
        if os.path.exists(cache_file):
            os.remove(cache_file)
        return None


def save_to_cache(cache_file: str, data: Dict[str, Any]) -> None:
    """Save data to cache with timestamp."""
    ensure_cache_dir()

    cached_data = {
        **data,
        "cache_timestamp": datetime.now().isoformat(),
        "cache_expires_at": (
            datetime.now() + timedelta(seconds=CACHE_DURATION)
        ).isoformat(),
    }

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cached_data, f, ensure_ascii=False, indent=2)


async def get_companylist_with_cache(domain: str) -> Dict[str, Any]:
    """Get company list with caching."""
    cache_key = f"{domain}_companylist"
    cache_file = COMPANY_CACHE_FILE

    # Try to load from cache first
    cached_data = load_cached_data(cache_file)
    if cached_data and cached_data.get("domain") == domain:
        print(f"Using cached data for domain: {domain}")
        cached_data["from_cache"] = True
        cached_data["cache_hit"] = True
        return cached_data

    # If not in cache or expired, fetch new data
    print(f"Cache miss for domain: {domain}, fetching new data...")
    start_time = time.perf_counter()
    result = await scrape_downdetector_links(domain)
    end_time = time.perf_counter()

    duration = round(end_time - start_time, 3)

    if not result:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from Downdetector"
        )

    # Prepare response
    response_data = {
        "duration_seconds": duration,
        "domain": domain,
        "cache_timestamp": datetime.now().isoformat(),
        "cache_expires_at": (
            datetime.now() + timedelta(seconds=CACHE_DURATION)
        ).isoformat(),
        "from_cache": False,
        "cache_hit": False,
    }

    # Add result based on type
    if isinstance(result, dict):
        response_data.update(result)
    else:
        response_data["companies"] = result

    # Save to cache
    save_to_cache(cache_file, response_data)

    return response_data


# Status endpoint cache (for individual company status)
async def get_status_with_cache(
    company: str, domain: str, timezone: str
) -> Dict[str, Any]:
    """Get status with caching for individual companies."""
    ensure_cache_dir()

    # Create a unique cache key for this company/domain/timezone combination
    cache_key = f"{company}_{domain}_{timezone}".replace("/", "_").replace(":", "_")
    cache_file = os.path.join(CACHE_DIR, f"status_{cache_key}.json")

    # Try to load from cache first
    cached_data = load_cached_data(cache_file)
    if cached_data:
        print(f"Using cached status for {company} on {domain}")
        cached_data["from_cache"] = True
        cached_data["cache_hit"] = True
        return cached_data

    # If not in cache or expired, fetch new data
    print(f"Cache miss for {company} on {domain}, fetching new data...")
    start_time = time.perf_counter()
    result = await downdetector(company, domain, timezone)
    end_time = time.perf_counter()

    duration = round(end_time - start_time, 3)

    if not result:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve data for {company}"
        )

    # Prepare response
    response_data = {
        "duration_seconds": duration,
        "company": company,
        "domain": domain,
        "timezone": timezone,
        "cache_timestamp": datetime.now().isoformat(),
        "cache_expires_at": (
            datetime.now() + timedelta(seconds=CACHE_DURATION)
        ).isoformat(),
        "from_cache": False,
        "cache_hit": False,
    }

    # Add result based on type
    if isinstance(result, dict):
        response_data.update(result)
    else:
        response_data["data"] = result

    # Save to cache
    save_to_cache(cache_file, response_data)

    return response_data


@app.get("/status")
async def get_status(
    company: str = Query(..., description="Company name on Downdetector"),
    domain: str = Query("com.br", description="Downdetector domain (default: com.br)"),
    timezone: str = Query(
        "America/Maceio",
        description="Timezone for timestamps (default: America/Maceio)",
    ),
):
    """Get service status for a specific company with caching."""
    return await get_status_with_cache(company, domain, timezone)


@app.get("/companylist")
async def get_companies(
    domain: str = Query("com.br", description="Downdetector domain (default: com.br)"),
):
    """Get list of companies with caching."""
    return await get_companylist_with_cache(domain)


@app.get("/cache/info")
async def get_cache_info():
    """Get information about the cache."""
    ensure_cache_dir()

    cache_files = []
    total_size = 0

    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CACHE_DIR, filename)
            file_stat = os.stat(filepath)

            cache_info = {
                "filename": filename,
                "size_bytes": file_stat.st_size,
                "size_mb": round(file_stat.st_size / (1024 * 1024), 3),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            }

            # Try to load cache metadata
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cache_info.update(
                        {
                            "cache_timestamp": data.get("cache_timestamp"),
                            "cache_expires_at": data.get("cache_expires_at"),
                            "from_cache": data.get("from_cache", False),
                            "domain": data.get("domain"),
                            "company": data.get("company"),
                        }
                    )
            except:
                pass

            cache_files.append(cache_info)
            total_size += file_stat.st_size

    return {
        "cache_directory": CACHE_DIR,
        "cache_duration_seconds": CACHE_DURATION,
        "cache_duration_minutes": CACHE_DURATION / 60,
        "total_files": len(cache_files),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 3),
        "files": cache_files,
    }


@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cache files."""
    ensure_cache_dir()

    cleared_files = []
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CACHE_DIR, filename)
            os.remove(filepath)
            cleared_files.append(filename)

    return {
        "message": "Cache cleared successfully",
        "cleared_files": cleared_files,
        "total_cleared": len(cleared_files),
    }


@app.delete("/cache/clear/expired")
async def clear_expired_cache():
    """Clear only expired cache files."""
    ensure_cache_dir()

    cleared_files = []
    current_time = datetime.now()

    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CACHE_DIR, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                expires_at_str = data.get("cache_expires_at")
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if current_time > expires_at:
                        os.remove(filepath)
                        cleared_files.append(filename)
            except:
                # If there's an error reading the file, remove it
                os.remove(filepath)
                cleared_files.append(filename)

    return {
        "message": "Expired cache cleared successfully",
        "cleared_files": cleared_files,
        "total_cleared": len(cleared_files),
    }


if __name__ == "__main__":
    # Ensure cache directory exists on startup
    ensure_cache_dir()

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
