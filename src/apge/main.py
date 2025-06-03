from fastapi import FastAPI, Body, Depends
from typing import List, Any, Optional # Dict removed as Pydantic models will be used for structured dicts
from pydantic import BaseModel
from neo4j import GraphDatabase, Session as Neo4jSession
import os

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

    # Placeholder for vector service call (S-3)
    print(f"Vector service call for IDs: {request_body.ids} - Placeholder for S-3") # Basic logging
    lit_chunks_data = [] # Dummy data

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

    return CompareResponse(
        table=TableResponse(columns=table_columns_list, data=table_data_rows),
        narrative_md="LLM-generated narrative will be here in S-3.",
        lit_chunks=lit_chunks_data
    )
