from datetime import datetime
from typing import Dict
from pyparsing import Any


def api_response(data: Any) -> Dict[str, Any]:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+06:00")
    return {
        "success": True,
        "data": data,
        "timestamp": timestamp
    }