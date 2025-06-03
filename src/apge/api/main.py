import yaml
from fastapi import FastAPI, HTTPException
from typing import Any
import os

# Create a FastAPI instance
app = FastAPI()

# Define the path to the protocols YAML file
# Adjust the path if necessary based on where the API is run from.
# This assumes the API is run from the project root or that src is in PYTHONPATH.
PROTOCOLS_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "protocols", "protocols.yaml")

@app.get("/protocols", response_model=Any) # Using Any for now, can be a Pydantic model later
async def get_protocols():
    """
    Reads protocol data from the YAML file and returns it.
    """
    if not os.path.exists(PROTOCOLS_FILE_PATH):
        raise HTTPException(status_code=404, detail="Protocols file not found.")

    try:
        with open(PROTOCOLS_FILE_PATH, 'r') as f:
            protocol_data = yaml.safe_load(f)
        if not protocol_data:
            # Handle empty YAML file case
            return {}
        return protocol_data
    except yaml.YAMLError:
        raise HTTPException(status_code=500, detail="Error parsing YAML file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Example of how to run this app with uvicorn (for development):
# uvicorn src.apge.api.main:app --reload --port 8000
