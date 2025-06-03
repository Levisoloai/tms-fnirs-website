import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase, Driver, ManagedTransaction, unit_of_work
from dataclasses import asdict

# Assuming graph_schema.py is in the same directory or PYTHONPATH is set up
from graph_schema import Diagnosis, Symptom, Target, StimParams, Evidence, SCHEMA_VERSION

# --- Configuration ---
# Configuration and database connection details are now primarily managed by scripts/seed.py
# However, load_dotenv() might still be useful if this module is used independently
# or if other scripts import from it and expect .env to be pre-loaded.
# For clarity, we'll keep it, but the seed script has its own .env loading.
load_dotenv()


class GraphDAO:
    def __init__(self, driver: Driver):
        self.driver = driver

    @staticmethod
    @unit_of_work(timeout=(5 * 60)) # 5 minute timeout
    def _execute_query(tx: ManagedTransaction, query: str, params: dict = None):
        result = tx.run(query, params or {})
        return [record for record in result]

    def apply_schema_constraints(self):
        """
        Applies uniqueness constraints to the Neo4j schema.
        These constraints help ensure data integrity and optimize queries.
        """
        print("Applying schema constraints...")
        constraint_queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Diagnosis) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Target) REQUIRE t.region IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (sp:StimParams) REQUIRE sp.unique_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Evidence) REQUIRE e.unique_id IS UNIQUE"
        ]
        with self.driver.session() as session:
            for query_string in constraint_queries:
                try:
                    print(f"Applying constraint: {query_string}")
                    session.execute_write(self._execute_query, query_string)
                    print(f"Successfully applied or verified constraint: {query_string.split('FOR')[1].split('REQUIRE')[0].strip()}")
                except Exception as e:
                    # This might catch errors if the constraint creation fails for reasons other than already existing
                    print(f"Error applying constraint {query_string}: {e}")
        print("Schema constraints application process complete.")

    def get_all_targets(self) -> List[Dict[str, str]]:
        """
        Fetches all distinct target regions from the graph.
        Filters by schema_version for consistency.
        """
        print("Fetching all distinct target regions...")
        query = "MATCH (t:Target) WHERE t.schema_version = $schema_version RETURN DISTINCT t.region AS region"
        # If schema_version is not critical or might be missing on some Target nodes:
        # query = "MATCH (t:Target) RETURN DISTINCT t.region AS region"

        with self.driver.session() as session:
            results = session.execute_read(self._execute_query, query, params={"schema_version": SCHEMA_VERSION})
            # For the alternative query without schema_version:
            # results = session.execute_read(self._execute_query, query)

        targets = [{"region": record["region"]} for record in results if record["region"] is not None]
        print(f"Found {len(targets)} distinct target regions.")
        return targets

    def clear_apge_graph(self):
        deletable_labels_str = os.environ.get("NEO4J_DELETABLE_LABELS")
        default_labels = ["Diagnosis", "Symptom", "Target", "StimParams", "Evidence"]

        labels_to_delete = []
        if deletable_labels_str:
            labels_to_delete = [label.strip() for label in deletable_labels_str.split(',') if label.strip()]
            if not labels_to_delete: # Handles case where env var is e.g. ",," or " "
                print("Warning: NEO4J_DELETABLE_LABELS was set but parsed to an empty list. Using default APGE labels for deletion.")
                labels_to_delete = default_labels
            else:
                print(f"NEO4J_DELETABLE_LABELS is set. Targeting the following labels for deletion: {labels_to_delete}")
        else:
            print("NEO4J_DELETABLE_LABELS not set. Using default APGE labels for deletion.")
            labels_to_delete = default_labels

        if not labels_to_delete:
            print("Warning: No labels specified or defaulted for deletion in clear_apge_graph. Skipping deletion.")
            return

        print(f"Clearing APGE graph data by deleting nodes with labels: {labels_to_delete}...")

        queries = []
        for label in labels_to_delete:
            # Basic sanity check for a label to prevent injection if source was less controlled
            if not label.isalnum():
                print(f"Warning: Skipping potentially invalid label '{label}' during clear_apge_graph.")
                continue
            queries.append(f"MATCH (n:{label}) DETACH DELETE n")

        if not queries:
            print("Warning: No valid queries constructed for deletion (all specified labels were potentially invalid). Skipping deletion.")
            return

        # Old query:
        # "MATCH (n) WHERE n.schema_version IS NOT NULL DETACH DELETE n"

        with self.driver.session() as session:
            for query in queries:
                print(f"Executing: {query}") # Good to log what's being run
                try:
                    session.execute_write(self._execute_query, query)
                except Exception as e:
                    print(f"Error executing query '{query}': {e}")
                    # Decide if you want to continue with other queries or stop.
                    # For now, it will continue.
        print("Graph clearing process completed for specified labels.")

    # Upsert methods for nodes
    def add_node(self, tx: ManagedTransaction, label: str, properties: Dict[str, Any], primary_key: str = "name"):
        prop_str = ", ".join([f"n.{key} = $props.{key}" for key in properties if key != primary_key and key != 'schema_version'])
        
        # Ensure primary_key property is part of prop_str for ON CREATE if it's not empty
        create_prop_str = f"n.{primary_key} = $props.{primary_key}"
        if prop_str:
            create_prop_str += f", {prop_str}"

        query = (
            f"MERGE (n:{label} {{{primary_key}: $props.{primary_key}}}) "
            f"ON CREATE SET {create_prop_str}, n.schema_version = $schema_version "
            f"ON MATCH SET {prop_str}, n.schema_version = $schema_version " # Ensure update on match too, primary key doesn't change
            "RETURN n"
        )
        
        node_props = properties.copy()
        if 'schema_version' in node_props: # schema_version is handled separately by $schema_version
            del node_props['schema_version']

        result = tx.run(query, props=node_props, schema_version=SCHEMA_VERSION)
        return result.single()[0]


    def add_relationship(self, tx: ManagedTransaction, from_label: str, from_props: Dict[str, Any],
                         to_label: str, to_props: Dict[str, Any], rel_type: str,
                         from_primary_key: str = "name", to_primary_key: str = "name"):
        query = (
            f"MATCH (a:{from_label} {{{from_primary_key}: $from_val}}), (b:{to_label} {{{to_primary_key}: $to_val}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "RETURN type(r)"
        )
        tx.run(query, from_val=from_props[from_primary_key], to_val=to_props[to_primary_key])

    def process_database(self, db_dict: Dict[str, Any]):
        with self.driver.session() as session:
            for diagnosis_name, symptoms_data in db_dict.items():
                diag_props = asdict(Diagnosis(name=diagnosis_name))
                
                session.execute_write(self.add_node_tx, "Diagnosis", diag_props)

                for symptom_name, params_data in symptoms_data.items():
                    sympt_props = asdict(Symptom(name=symptom_name))
                    session.execute_write(self.add_node_tx, "Symptom", sympt_props)
                    session.execute_write(self.add_relationship_tx, "Diagnosis", diag_props, "Symptom", sympt_props, "HAS_SYMPTOM")

                    target_name = params_data.get('target')
                    target_props = asdict(Target(region=target_name)) # Assuming mni_coords might be added later
                    session.execute_write(self.add_node_tx, "Target", target_props, primary_key="region")
                    session.execute_write(self.add_relationship_tx, "Symptom", sympt_props, "Target", target_props, "TARGETED_BY", to_primary_key="region")
                    
                    # Create StimParams node properties
                    stim_params_obj = StimParams(
                        pattern=params_data.get('frequency'), # 'frequency' field seems to map to 'pattern'
                        pulses=params_data.get('pulses'),
                        intensity_pct=float(str(params_data.get('intensity', '0% MT')).replace('% MT', '').replace('% AMT', '').strip()), # Basic parsing
                        sessions=str(params_data.get('sessions'))
                    )
                    stim_params_props = asdict(stim_params_obj)
                    # StimParams might not have a simple unique 'name'. We need a composite key or unique ID.
                    # For now, we'll merge based on all its core properties to ensure uniqueness.
                    # This requires a different add_node_tx or modification.
                    # Let's define a unique_id for StimParams for simplicity in MERGE.
                    stim_unique_id = f"{target_name}_{stim_params_obj.pattern}_{stim_params_obj.pulses}_{stim_params_obj.intensity_pct}_{stim_params_obj.sessions}"
                    stim_params_props_with_id = {**stim_params_props, "unique_id": stim_unique_id}

                    session.execute_write(self.add_node_tx, "StimParams", stim_params_props_with_id, primary_key="unique_id")
                    session.execute_write(self.add_relationship_tx, "Target", target_props, "StimParams", stim_params_props_with_id, "USUALLY_TREATED_WITH", from_primary_key="region", to_primary_key="unique_id")

                    evidence_obj = Evidence(
                        level=params_data.get('evidence'),
                        references=params_data.get('references', []),
                        notes=params_data.get('notes')
                    )
                    evidence_props = asdict(evidence_obj)
                    # Evidence also needs a unique identifier for MERGE if not just linking to one StimParams
                    # For now, assume evidence is specific to this StimParams instance.
                    # If evidence can be shared, it needs its own unique properties for MERGE.
                    # Let's create a unique_id for Evidence as well.
                    evidence_unique_id = f"ev_{stim_unique_id}_{evidence_obj.level}"
                    if evidence_obj.references: # Add first reference to unique ID if exists
                        evidence_unique_id += f"_{evidence_obj.references[0][:20]}" # first 20 chars of first ref
                    
                    evidence_props_with_id = {**evidence_props, "unique_id": evidence_unique_id}

                    session.execute_write(self.add_node_tx, "Evidence", evidence_props_with_id, primary_key="unique_id")
                    session.execute_write(self.add_relationship_tx, "StimParams", stim_params_props_with_id, "Evidence", evidence_props_with_id, "SUPPORTED_BY", from_primary_key="unique_id", to_primary_key="unique_id")
            print("Database processing complete.")

    # Transactional versions of add_node and add_relationship for use within session.execute_write
    def add_node_tx(self, tx: ManagedTransaction, label: str, properties: Dict[str, Any], primary_key: str = "name"):
        return self.add_node(tx, label, properties, primary_key) # Calls the static method logic

    def add_relationship_tx(self, tx: ManagedTransaction, from_label: str, from_props: Dict[str, Any],
                         to_label: str, to_props: Dict[str, Any], rel_type: str,
                         from_primary_key: str = "name", to_primary_key: str = "name"):
        return self.add_relationship(tx, from_label, from_props, to_label, to_props, rel_type, from_primary_key, to_primary_key)

# The main() function and direct script execution logic have been moved to scripts/seed.py
# The PROTOCOL_DATABASE_PYTHON dictionary has been moved to src/apge/protocols/protocols.yaml
