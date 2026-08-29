import os
from fastapi import Header, HTTPException

API_KEY_ENABLED = os.environ.get("API_KEY_ENABLED", "false").lower() == "true"
API_KEY = os.environ.get("API_KEY")


async def verify_api_key(x_api_key: str = Header(default=None)):
    """
    Toggleable API key check. Disabled by default (API_KEY_ENABLED=false)
    so the public portfolio demo stays freely browsable via /docs.
    Set API_KEY_ENABLED=true and API_KEY=<some secret> to lock it down
    for a real deployment.
    """
    if not API_KEY_ENABLED:
        return
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY_ENABLED is true but API_KEY is not set")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
