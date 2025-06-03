from fastapi import FastAPI, Body
from typing import List, Dict, Any

app = FastAPI() # Assuming your FastAPI app instance is named 'app'

@app.get("/api/protocol/list")
async def list_protocols(diagnosis: str = ""):
    # Dummy data for now
    return [
        {"id": "p1", "label": "Protocol 1", "device": "Device A", "evidence_level": "High"},
        {"id": "p2", "label": "Protocol 2", "device": "Device B", "evidence_level": "Medium"},
    ]

@app.post("/api/protocol/compare")
async def compare_protocols(ids: List[str] = Body(..., embed=True)):
    # Dummy data for now
    return {
        "table": {
            "columns": ["Protocol", "Coil Type", "Frequency", "Intensity"],
            "data": [
                ["Protocol 1", "Figure-8", "10Hz", "120% RMT"],
                ["Protocol 2", "H-Coil", "20Hz", "110% RMT"],
            ]
        },
        "narrative_md": "This is a placeholder narrative comparing the selected protocols."
    }
