from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any

# --- Import the single logger ---
from logger import logger

# --- A Single, Flexible Pydantic Model ---
# This model accepts all possible fields from all 3 event types.
# All fields are Optional to prevent errors if one event type
# doesn't have a field (e.g., a "publish" event won't have "topic").

class WebhookEvent(BaseModel):
    # Common fields
    clientid: Optional[str] = None
    username: Optional[str] = None
    timestamp: Optional[int] = None
    ip_address: Optional[str] = None  # From 'peername AS ip_address'
    event: Optional[str] = None       # From '$events/...'
    
    # Connect/Disconnect specific
    connected_at: Optional[int] = None
    disconnected_at: Optional[int] = None
    reason: Optional[str] = None

    # Publish specific
    topic: Optional[str] = None
    payload: Optional[Any] = None

# --- Create the Router ---
router = APIRouter()

# --- Create the Single Endpoint ---
# All rules should now point to POST /logs/webhook
@router.post("/webhook")
async def handle_webhook(log_entry: WebhookEvent):
    
    # Convert the Pydantic model to a dictionary.
    # exclude_unset=True is the magic: it *only* includes fields
    # that were actually sent by EMQX for this specific event.
    data_dict = log_entry.model_dump(exclude_unset=True)

    # Handle the payload separately to avoid cluttering the log
    payload = data_dict.pop("payload", None)

    # Format all other data into a single string: "key1=value1 | key2=value2"
    log_parts = [f"{key}={value}" for key, value in data_dict.items()]
    log_message = " | ".join(log_parts)

    # Add the payload back if it existed
    if payload is not None:
        log_message += f" | payload={payload}"

    # Write the merged log message to the file and print to console
    logger.info(log_message)
    print(f"📡 [WEBHOOK] {log_message}")
        
    return {"status": "ok", "message": "webhook received"}
