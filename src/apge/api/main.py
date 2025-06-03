import yaml
from fastapi import FastAPI, HTTPException
from typing import Any, List
import os
import asyncio # Added for asyncio.to_thread

from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver
from src.apge.etl import GraphDAO
# Assuming graph_schema.py is in the same directory or PYTHONPATH is set up
# For SCHEMA_VERSION to be available if GraphDAO methods need it directly,
# though it's encapsulated within GraphDAO itself.
# from src.apge.graph_schema import SCHEMA_VERSION

from .models import TargetsListOutput, TargetOutput, PatientDataInput, RecommendationOutput, ProtocolDetail
from .static_data import all_static_data_for_api # Import from static_data.py

# Determine project root to correctly locate .env and other src files
# __file__ is src/apge/api/main.py
# os.path.dirname(__file__) is src/apge/api
# os.path.dirname(os.path.dirname(__file__)) is src/apge
# os.path.dirname(os.path.dirname(os.path.dirname(__file__))) is src/
# os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) is project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file from src/apge/.env
dotenv_path = os.path.join(PROJECT_ROOT, 'src', 'apge', '.env')
print(f"Attempting to load .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USER = os.environ.get("NEO4J_USER")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

driver: Optional[Driver] = None
dao: Optional[GraphDAO] = None

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    print("Warning: NEO4J_URI, NEO4J_USER, or NEO4J_PASSWORD not found in environment. "
          "Database-dependent endpoints will fail if not configured via another method.")
else:
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # It's good practice to verify connectivity, perhaps in a startup event
        # driver.verify_connectivity()
        dao = GraphDAO(driver)
        print("Neo4j driver and DAO initialized for API.")
    except Exception as e:
        print(f"Failed to initialize Neo4j driver or DAO: {e}")
        driver = None
        dao = None

# Create a FastAPI instance
app = FastAPI()

@app.on_event("shutdown")
async def shutdown_event():
    if driver:
        driver.close()
        print("Neo4j driver closed.")

# Define the path to the protocols YAML file
# Adjust the path if necessary based on where the API is run from.
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


@app.get("/targets", response_model=TargetsListOutput)
async def get_targets_list():
    if not dao:
        # This check might be redundant if using lifespan events to ensure DAO or raise startup error
        raise HTTPException(status_code=503, detail="Database service not available. DAO not initialized.")
    if not driver: # Or check driver.is_closed() if applicable and a more robust check
        raise HTTPException(status_code=503, detail="Database connection not available.")

    try:
        # Run synchronous DAO method in a separate thread to avoid blocking event loop
        target_dicts = await asyncio.to_thread(dao.get_all_targets)

        # Transform the list of dictionaries into a list of TargetOutput Pydantic models
        targets_output = [TargetOutput(region=item['region']) for item in target_dicts]

        return TargetsListOutput(targets=targets_output)
    except Exception as e:
        print(f"Error retrieving targets: {e}") # Log the error server-side
        # Consider more specific error checks, e.g., for Neo4j connection issues
        raise HTTPException(status_code=500, detail=f"Failed to retrieve targets: {str(e)}")

# Placeholder 'all_static_data_placeholder' is now removed, using import from .static_data

def load_protocol_data_internal() -> dict:
    """
    Loads protocol data from the YAML file.
    Internal version for use by other endpoints.
    """
    if not os.path.exists(PROTOCOLS_FILE_PATH):
        # Log this error as it's a server configuration issue
        print(f"CRITICAL: Protocols file not found at {PROTOCOLS_FILE_PATH}")
        raise HTTPException(status_code=500, detail="Protocols file not found. Server configuration error.")
    try:
        with open(PROTOCOLS_FILE_PATH, 'r') as f:
            protocol_data = yaml.safe_load(f)
        return protocol_data if protocol_data else {}
    except yaml.YAMLError as e:
        print(f"CRITICAL: Error parsing YAML file at {PROTOCOLS_FILE_PATH}: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing protocol data: {str(e)}")
    except Exception as e:
        print(f"CRITICAL: Unexpected error loading protocol data from {PROTOCOLS_FILE_PATH}: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error loading protocol data: {str(e)}")

def generate_recommendations_py(patient_data: PatientDataInput, protocol_db: dict, static_lists: dict) -> RecommendationOutput:
    """
    Generates TMS protocol recommendations based on patient data and protocol database.
    Ported from JavaScript logic.
    """
    primary_diagnosis = patient_data.primaryDiagnosis
    selected_symptoms = patient_data.symptoms if patient_data.symptoms else []
    # severity = patient_data.severity # Not used in the JS logic directly for protocol selection
    age_str = patient_data.age
    # medication_resistant = patient_data.medicationResistant # Not used in the simple JS logic shown
    selected_comorbidities = patient_data.comorbidities if patient_data.comorbidities else []
    selected_previous_treatments = patient_data.previousTreatments if patient_data.previousTreatments else []
    specific_contraindications = patient_data.specificContraindications if patient_data.specificContraindications else []

    # Initialize RecommendationOutput fields
    primary_protocol_out: Optional[ProtocolDetail] = None
    alternative_protocols_out: List[ProtocolDetail] = []
    modifications: List[str] = []
    safety_considerations: List[str] = []
    monitoring: List[str] = []
    expected_outcomes: Dict[str, str] = {} # Example: {"symptom_reduction": "Expected within 2-4 weeks"}
    warnings: List[str] = []

    if not primary_diagnosis or not protocol_db.get(primary_diagnosis):
        warnings.append(f"No protocols found for diagnosis: {primary_diagnosis or 'Not provided'}.")
        # Return early if no diagnosis or no protocols for diagnosis
        return RecommendationOutput(
            primary=primary_protocol_out,
            alternatives=alternative_protocols_out,
            modifications=modifications,
            safetyConsiderations=safety_considerations,
            monitoring=monitoring,
            expectedOutcomes=expected_outcomes,
            warnings=warnings
        )

    diagnosis_protocols = protocol_db[primary_diagnosis]

    # Determine primary protocol based on the first selected symptom
    if selected_symptoms:
        primary_symptom = selected_symptoms[0]
        if diagnosis_protocols.get(primary_symptom):
            proto_data = diagnosis_protocols[primary_symptom]
            primary_protocol_out = ProtocolDetail(symptom=primary_symptom, **proto_data)
        else:
            warnings.append(f"No specific protocol found for primary symptom '{primary_symptom}' in diagnosis '{primary_diagnosis}'.")
            # Fallback: Maybe suggest a general protocol for the diagnosis if available? (Not in JS logic)

    # Determine alternative protocols for other selected symptoms
    if len(selected_symptoms) > 1:
        for alt_symptom in selected_symptoms[1:]:
            if diagnosis_protocols.get(alt_symptom):
                alt_proto_data = diagnosis_protocols[alt_symptom]
                alternative_protocols_out.append(ProtocolDetail(symptom=alt_symptom, **alt_proto_data))

    # Adjustments / Modifications (based on the simple JS logic)
    # These are general and not tied to a specific protocol in the JS version.
    if "Anxiety" in selected_comorbidities: # Assuming "Anxiety" is a string from static_lists eventually
        # This was tied to "Left DLPFC" in JS, making it general here for simplicity:
        modifications.append("If Left DLPFC is targeted, consider lower intensity or shorter duration due to anxiety comorbidity.")

    if "ECT" in selected_previous_treatments: # Assuming "ECT" is a string
        modifications.append("May require motor threshold re-assessment post-ECT.")

    patient_age_int = -1
    if age_str:
        try:
            patient_age_int = int(age_str)
        except ValueError:
            warnings.append(f"Patient age '{age_str}' is not a valid number.")

    if patient_age_int > 65:
        modifications.append("Consider age: potential need for intensity adjustment or closer monitoring (e.g., start 100-110% MT).")

    # Default safety, monitoring, outcomes (can be made more dynamic)
    safety_considerations.extend([
        "Ensure proper coil placement and MT determination.",
        "Monitor for headache, scalp discomfort, or twitching.",
        "Risk of seizure is rare but present; follow screening protocols."
    ])
    monitoring.extend([
        "Weekly symptom ratings (e.g., PHQ-9, GAD-7).",
        "Monitor side effects at each session.",
        "Assess clinical response every 10 sessions."
    ])
    if primary_protocol_out: # Base expected outcomes on primary protocol if available
        expected_outcomes["general_timeline"] = "Initial response may be seen in 2-4 weeks, with full effect typically after 4-6 weeks."
        expected_outcomes["target_symptom_improvement"] = f"Reduction in '{primary_protocol_out.symptom}' severity."


    # Contraindications warning
    if specific_contraindications:
        contra_warning = "The following potential contraindications were identified by the user: " + ", ".join(specific_contraindications)
        warnings.append(contra_warning)
        warnings.append("Please thoroughly evaluate ALL contraindications before proceeding with TMS treatment. This tool does not perform a full contraindication screening.")

    # If no primary protocol could be determined, add a general note to warnings
    if not primary_protocol_out and not warnings: # Avoid duplicate warnings if already added one for diagnosis
        warnings.append("Could not determine a specific primary protocol based on input. Please review clinical guidelines.")


    return RecommendationOutput(
        primary=primary_protocol_out,
        alternatives=alternative_protocols_out,
        modifications=modifications,
        safetyConsiderations=safety_considerations,
        monitoring=monitoring,
        expectedOutcomes=expected_outcomes,
        warnings=warnings
    )

@app.post("/recommendations", response_model=RecommendationOutput)
async def get_recommendations_api(patient_input: PatientDataInput):
    protocol_data = load_protocol_data_internal()

    # Using imported static data
    static_payload = all_static_data_for_api

    try:
        # Run synchronous recommendation logic in a separate thread
        # to avoid blocking the FastAPI event loop.
        recommendations = await asyncio.to_thread(
            generate_recommendations_py,
            patient_input,
            protocol_data,
            static_payload
        )
        return recommendations
    except HTTPException:
        raise # Re-raise HTTPExceptions from load_protocol_data_internal
    except Exception as e:
        print(f"Error generating recommendations: {e}") # Log the full error server-side
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating recommendations: {str(e)}")
