from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather", log_level="ERROR") 

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather/0.1 (https://github.com/zwx-c/weather)"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper headers.

    Args:
        url: The URL to request.

    Returns:
        The JSON response as a dictionary, or None if the request failed.
    """

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

def format_alert(feature: dict) -> str:
    """Format a weather alert feature into a human-readable string.

    Args:
        feature: The weather alert feature dictionary.

    Returns:
        A formatted string representing the weather alert.
    """
    props = feature["properties"]
    return f"""
    Event: {props.get("event", "Unknown")}
    Headline: {props.get("headline", "No Headline")}
    Description: {props.get("description", "No Description")}
    """

async def get_alerts(state: str) -> str:
    """Get weather alerts for a given state.

    Args:
        state: The state abbreviation (e.g., "CA" for California).

    Returns:
        A formatted string of weather alerts for the state.
    """
    url = f"{NWS_API_BASE}/points/{state}:{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Failed to fetch alert data."
    if not data["features"]:
        return "No weather alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    
    return "\n\n".join(alerts)