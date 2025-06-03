from fastapi import FastAPI, Body, Depends
from typing import List, Any, Optional
from pydantic import BaseModel
from neo4j import GraphDatabase, Session as Neo4jSession
import os
import json # Added for OpenAI prompt data formatting
from openai import OpenAI # Added for OpenAI integration
import redis # Added for Redis caching
import hashlib # Added for cache key generation

# Pydantic Models
class ProtocolCard(BaseModel):
    id: str
    label: str
    device: Optional[str] = None
    evidence_level: Optional[str] = None

class CompareRequest(BaseModel):
    ids: List[str]

class TableResponse(BaseModel):
    columns: List[str]
    data: List[List[Any]] # Using Any for mixed-type rows, as cell types can vary

class CompareResponse(BaseModel):
    table: TableResponse
    narrative_md: str
    lit_chunks: List[Any] # Define more specifically if lit_chunks structure is known, using Any for now

# Redis Client Setup
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

redis_client = None
try:
    temp_redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0, decode_responses=True)
    temp_redis_client.ping()
    redis_client = temp_redis_client # Assign to global only if connection successful
    print("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}. Caching will be disabled.")
    # redis_client remains None

# Neo4j Driver Setup
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password") # Replace with a more secure default or ensure it's always set

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_db() -> Neo4jSession: # Changed type hint for clarity
    session = None
    try:
        session = driver.session()
        yield session
    finally:
        if session:
            session.close()

app = FastAPI()

@app.get("/api/protocol/list", response_model=List[ProtocolCard])
async def list_protocols(diagnosis: Optional[str] = None, db: Neo4jSession = Depends(get_db)):
    # Base query to fetch protocol details
    # Using OPTIONAL MATCH for device and evidence to ensure protocols are returned even if these are missing
    # Assuming Protocol nodes are labeled :Protocol and have 'id' and 'name' properties
    # Assuming Device nodes are labeled :Device and have 'name'
    # Assuming Evidence nodes are labeled :Evidence and have 'level'
    # Relationships:
    #   (Protocol)-[:USES_STIMPARAMS]->(:StimParams)-[:DELIVERED_BY]->(Device)
    #   (Protocol)-[:HAS_EVIDENCE]->(Evidence)
    #   (Protocol)-[:HAS_INDICATION]->(Diagnosis) where Diagnosis has 'name'

    query_parts = [
        "MATCH (p:Protocol)",
        "OPTIONAL MATCH (p)-[:USES_STIMPARAMS]->()-[:DELIVERED_BY]->(dev:Device)",
        "OPTIONAL MATCH (p)-[:HAS_EVIDENCE]->(e:Evidence)",
    ]
    params = {}

    if diagnosis:
        query_parts.append("MATCH (p)-[:HAS_INDICATION]->(d:Diagnosis)")
        # Using toLower for case-insensitive matching on diagnosis name
        query_parts.append("WHERE toLower(d.name) = toLower($diagnosis) OR toLower(d.subtype) = toLower($diagnosis)")
        params["diagnosis"] = diagnosis

    # Collect distinct protocols with their associated, potentially multiple, devices and evidences
    # Then, for each protocol, collect its devices and evidences into lists.
    # This avoids issues with cartesian products from multiple OPTIONAL MATCHes if a protocol has multiple devices/evidences.
    # However, the schema implies one device and one evidence level per protocol in the output.
    # For simplicity in this step, we'll take the first device and first evidence found.
    # A more robust solution might involve collecting and choosing one, or ensuring data model guarantees singularity.

    # Simpler approach: get core protocol info, then device and evidence.
    # If a protocol is linked to multiple devices or evidences, this will pick one.
    query_parts.append(
        "RETURN p.id AS id, p.name AS label, dev.name AS device, e.level AS evidence_level"
    )

    query = " ".join(query_parts)

    results = db.run(query, params)

    # Process results: due to OPTIONAL MATCH, a protocol might appear multiple times
    # if it's linked to multiple devices or evidences. We need to consolidate.
    # However, the target output is one device and one evidence_level per protocol.
    # The query above will give one row per combination.
    # Example: P1 -> D1, E1 and P1 -> D1, E2 would give two rows.
    # We need to be careful. For now, the query is simplified and might need refinement
    # based on actual graph structure and desired aggregation if multiple are present.

    # Given the target output structure, the query should ideally return one row per protocol.
    # Let's refine the query to achieve that, taking the first found related node.
    # This is a common simplification if the data model isn't strictly 1-to-1 for these.

    final_query = """
    MATCH (p:Protocol)
    OPTIONAL MATCH (p)-[:USES_STIMPARAMS]->()-[:DELIVERED_BY]->(dev:Device)
    OPTIONAL MATCH (p)-[:HAS_EVIDENCE]->(e:Evidence)
    WITH p, dev, e
    """

    filter_clause = ""
    if diagnosis:
        # This WHERE clause applies after the OPTIONAL MATCHes for device/evidence,
        # but before the final RETURN. It filters protocols based on diagnosis.
        # To ensure we only get protocols that HAVE the indication if diagnosis is specified:
        final_query = """
        MATCH (p:Protocol)-[:HAS_INDICATION]->(d:Diagnosis)
        WHERE toLower(d.name) = toLower($diagnosis) OR (d.subtype IS NOT NULL AND toLower(d.subtype) = toLower($diagnosis))
        OPTIONAL MATCH (p)-[:USES_STIMPARAMS]->()-[:DELIVERED_BY]->(dev:Device)
        OPTIONAL MATCH (p)-[:HAS_EVIDENCE]->(e:Evidence)
        WITH p, d, dev, e
        """ # Ensure d is carried over if needed, or just p
        params = {"diagnosis": diagnosis}
    else:
        params = {}

    final_query += """
    RETURN p.id AS id, p.name AS label,
           COLLECT(DISTINCT dev.name)[0] AS device,
           COLLECT(DISTINCT e.level)[0] AS evidence_level
    ORDER BY p.name
    """
    # Using COLLECT(DISTINCT ...)[0] to pick one if multiple exist.
    # If dev or e is null for a protocol, their respective fields will be null.

    records = db.run(final_query, params)

    # FastAPI will automatically convert the list of dicts to List[ProtocolCard]
    # if the keys match the model fields.
    protocols_data = [
        ProtocolCard(
            id=record["id"],
            label=record["label"],
            device=record["device"],
            evidence_level=record["evidence_level"]
        ) for record in records
    ]
    return protocols_data

@app.post("/api/protocol/compare", response_model=CompareResponse)
async def compare_protocols(request_body: CompareRequest, db: Neo4jSession = Depends(get_db)):
    if not request_body.ids:
        # Return a CompareResponse-compatible structure
        return CompareResponse(
            table=TableResponse(columns=[], data=[]),
            narrative_md="No protocol IDs provided for comparison.",
            lit_chunks=[]
        )

    # Placeholder for vector service call (S-3) - This remains a placeholder for now
    # print(f"Vector service call for IDs: {request_body.ids} - Placeholder for S-3") # Basic logging
    lit_chunks_data = [] # Dummy data, actual data would come from vector service

    # Sort IDs for deterministic cache key
    sorted_ids = sorted(request_body.ids)
    ids_string = ",".join(sorted_ids)
    cache_key = f"narrative:{hashlib.md5(ids_string.encode('utf-8')).hexdigest()}"

    cached_narrative = None
    if redis_client:
        try:
            cached_narrative = redis_client.get(cache_key)
            if cached_narrative:
                print(f"Cache hit for key: {cache_key}")
        except redis.exceptions.RedisError as e:
            print(f"Redis GET command failed for key {cache_key}: {e}") # Log error, don't let it crash
            # If Redis fails, proceed as if cache miss, redis_client might be set to None by a more robust health check elsewhere
            # For now, just log and continue.

    narrative_to_return = cached_narrative # Will be None if cache miss or Redis error

    # Cypher query to fetch details for each protocol
    # Relationships:
    # (p:Protocol)-[:USES_STIMPARAMS]->(sp:StimParams)
    # (sp:StimParams)-[:DELIVERED_BY]->(d:Device)
    # (p:Protocol)-[:HAS_EVIDENCE]->(e:Evidence)
    query = """
    UNWIND $ids AS protocol_id
    MATCH (p:Protocol {id: protocol_id})
    OPTIONAL MATCH (p)-[:USES_STIMPARAMS]->(sp:StimParams)
    OPTIONAL MATCH (sp)-[:DELIVERED_BY]->(dev:Device)
    OPTIONAL MATCH (p)-[:HAS_EVIDENCE]->(e:Evidence)
    RETURN
        p.id AS protocol_id,
        p.name AS protocol_name,
        sp.pattern AS frequency,         // e.g., "10 Hz", "iTBS"
        sp.intensity_pct AS intensity,   // e.g., 120.0
        sp.pulses AS pulses_per_session, // e.g., 3000
        sp.sessions AS num_sessions,     // e.g., "20-30" or 20
        dev.name AS device_name,
        dev.coil_type AS coil_type,
        dev.manufacturer AS manufacturer,
        e.level AS evidence_level,
        e.pub_year AS publication_year,
        CASE WHEN size(e.references) > 0 THEN e.references[0] ELSE null END AS reference_doi
        // Taking the first reference as a placeholder for DOI/main reference
    """

    results = db.run(query, ids=request_body.ids)

    table_data_rows = []
    for record in results:
        table_data_rows.append([
            record["protocol_name"],
            record["coil_type"],
            record["frequency"],
            f"{record['intensity']}%" if record['intensity'] is not None else None, # Formatting intensity
            record["pulses_per_session"],
            record["num_sessions"],
            record["evidence_level"],
            record["device_name"],
            record["manufacturer"],
            record["publication_year"],
            record["reference_doi"]
        ])

    # Define table columns - ensure order matches data appended above
    table_columns_list = [
        "Protocol Name", "Coil Type", "Frequency", "Intensity",
        "Pulses/Session", "Sessions", "Evidence Level", "Device Name",
        "Manufacturer", "Publication Year", "Reference/DOI"
    ]

    # Prepare data for LLM
    protocols_json_list = []
    for row in table_data_rows:
        protocol_dict = dict(zip(table_columns_list, row))
        protocols_json_list.append(protocol_dict)

    protocols_details_str = json.dumps(protocols_json_list, indent=2)
    literature_abstracts_str = "\n\n".join(lit_chunks_data) if lit_chunks_data else "No specific literature abstracts provided for this comparison."

    if narrative_to_return is None: # Cache miss or Redis unavailable/error during GET
        print(f"Cache miss or Redis error for key: {cache_key}. Proceeding to generate narrative.")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("OPENAI_API_KEY not found. Skipping LLM narrative generation.")
            narrative_to_return = "Narrative generation is currently unavailable (API key not configured)."
        elif not protocols_json_list: # Don't call LLM if there's no protocol data
            narrative_to_return = "No protocol data found to generate a comparison narrative."
        else:
            try:
                client = OpenAI(api_key=openai_api_key)
                system_prompt = """You are a neuro-psychiatry protocol analyst. Your task is to compare and contrast treatment protocols based on the provided data. Focus on:
1.  Coil physics and its implications (e.g., focality, depth of penetration).
2.  Session burden on patients (e.g., frequency, duration, total number of sessions).
3.  Strength of clinical evidence (e.g., study types, sample sizes, effect sizes if available, level of evidence).

Please ensure your analysis is based *only* on the information given in the JSON data and literature abstracts. Do not infer or add external knowledge.
Structure your output as three distinct paragraphs addressing these aspects.
Conclude with a single, concise "Clinical Pearl" (1 sentence) offering a practical takeaway for a clinician choosing between these protocols.
Format the output as Markdown.
"""
            user_prompt = f"""Here are {len(protocols_json_list)} protocols as JSON:
```json
{protocols_details_str}
```

And here are {len(lit_chunks_data)} literature abstracts:
```text
{literature_abstracts_str}
```

Please provide a 3-paragraph compare-and-contrast analysis focusing on coil physics, session burden, and evidence strength, followed by a 1-sentence clinical pearl.
"""
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    model="gpt-3.5-turbo",
                )
                narrative_to_return = chat_completion.choices[0].message.content

                # Cache the new narrative if successfully generated and Redis is available
                if redis_client and narrative_to_return and \
                   not narrative_to_return.startswith("Error") and \
                   not narrative_to_return.startswith("Narrative generation is currently unavailable") and \
                   not narrative_to_return.startswith("No protocol data found"):
                    try:
                        redis_client.set(cache_key, narrative_to_return, ex=3600) # Cache for 1 hour
                        print(f"Cached new narrative for key: {cache_key}")
                    except redis.exceptions.RedisError as e:
                        print(f"Redis SET command failed for key {cache_key}: {e}") # Log error, don't let it crash
            except Exception as e:
                print(f"OpenAI API call failed: {e}")
                narrative_to_return = "Error generating narrative. Please try again later."

    return CompareResponse(
        table=TableResponse(columns=table_columns_list, data=table_data_rows),
        narrative_md=narrative_to_return, # Use the cached or newly generated narrative
        lit_chunks=lit_chunks_data
    )
