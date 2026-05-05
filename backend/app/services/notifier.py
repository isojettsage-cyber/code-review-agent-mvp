import httpx
from app.config import FEISHU_WEBHOOK_URL

async def notify_feishu(title: str, text: str) -> None:
    """Feishu webhook placeholder.

    To enable:
    1. Create a Feishu custom bot.
    2. Put the webhook URL into backend/.env as FEISHU_WEBHOOK_URL.
    3. Restart the backend.

    This MVP keeps notification failure non-blocking.
    """
    if not FEISHU_WEBHOOK_URL:
        print(f"[Feishu placeholder] {title}: {text}")
        return

    payload = {
        "msg_type": "text",
        "content": {
            "text": f"{title}\n{text}"
        },
    }

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(FEISHU_WEBHOOK_URL, json=payload)
    except Exception as exc:
        print(f"[Feishu notification failed] {exc}")
