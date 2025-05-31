import re
import asyncio
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime
from dateutil import parser
import pytz


async def call_downdetector(company: str, domain: str = "com.br") -> str:
    url = f"https://downdetector.{domain}/status/{company}/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        ))
        page = await context.new_page()
        await page.goto(url, timeout=30000)
        content = await page.content()
        await browser.close()
        return content


def get_script_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", {"type": "text/javascript"})
    for script in scripts:
        if script.string and "{ x:" in script.string:
            return script.string
    return ""


def extract_chart_lines(script: str) -> List[str]:
    return [line.strip() for line in script.split('\n') if "{ x:" in line]


def str2obj(chart_lines: List[str]) -> List[Dict[str, object]]:
    result = []
    for line in chart_lines:
        line = line.replace("{ ", "").replace(" },", "").replace("'", "")
        parts = line.split("x: ")[1].split(", y: ")
        result.append({
            "date": parts[0],
            "value": float(parts[1])
        })
    return result


def merge_chart_points(reports: List[Dict[str, object]], baseline: List[Dict[str, object]],
                       tz: Optional[str] = None) -> List[Dict[str, object]]:
    merged = []
    for rep, base in zip(reports, baseline):
        date_str = rep["date"]
        if tz:
            try:
                # Parse ISO 8601 and convert to target timezone
                iso_dt = parser.isoparse(date_str)
                target_tz = pytz.timezone(tz)
                date_str = iso_dt.astimezone(target_tz).strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"Timezone conversion error: {e}")
        merged.append({
            "date": date_str,
            "reports_value": rep["value"],
            "baseline_value": base["value"]
        })
    return merged


def get_reported_problems(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    problems = []

    indicators_card = soup.find("div", {"id": "indicators-card"})
    if not indicators_card:
        return problems

    col_blocks = indicators_card.select("div.col-4")

    for col in col_blocks:
        percentage_div = col.select_one(".indicatorChart_percentage")
        name_div = col.select_one(".indicatorChart_name")

        if percentage_div and name_div:
            percentage = percentage_div.get_text(strip=True).replace("%", "")
            name = name_div.get_text(strip=True)
            problems.append({
                "name": name,
                "percentage": f"{percentage}%"
            })

    return problems

def compute_summary_statistics(time_series: List[Dict[str, object]]) -> Dict[str, object]:
    if not time_series:
        return {}

    total_reports = sum(item["reports_value"] for item in time_series)
    average_reports = total_reports / len(time_series)

    max_reports_item = max(time_series, key=lambda x: x["reports_value"])
    max_deviation_item = max(time_series, key=lambda x: abs(x["reports_value"] - x["baseline_value"]))

    spikes = [item["date"] for item in time_series
              if item["reports_value"] > 2 * item["baseline_value"] and item["baseline_value"] > 0]

    alerts_count = sum(1 for item in time_series if item["reports_value"] > 1.5 * item["baseline_value"])

    return {
        "max_reports": {
            "value": max_reports_item["reports_value"],
            "timestamp": max_reports_item["date"]
        },
        "average_reports": round(average_reports, 2),
        "total_reports": round(total_reports),
        "max_deviation": {
            "value": abs(max_deviation_item["reports_value"] - max_deviation_item["baseline_value"]),
            "timestamp": max_deviation_item["date"]
        },
        "spikes": spikes,
        "alerts_count": alerts_count
    }


async def downdetector(company: str, domain: str = "com.br", timezone: Optional[str] = None) -> Dict[str, object]:
    html = await call_downdetector(company, domain)
    script_content = get_script_content(html)
    chart_lines = extract_chart_lines(script_content)

    reports = str2obj(chart_lines[:96])
    baseline = str2obj(chart_lines[96:192])
    time_series = merge_chart_points(reports, baseline, timezone)

    problems = get_reported_problems(html)

    return {
        "time_series": time_series,
        "most_reported_problems": problems,
        "stats": compute_summary_statistics(time_series)
    }


# Example usage
if __name__ == "__main__":
    import json
    result = asyncio.run(downdetector("pix", timezone="America/Maceio"))
    print(json.dumps(result, indent=2, ensure_ascii=False))
