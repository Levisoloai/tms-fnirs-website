import os
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase, Driver, ManagedTransaction, unit_of_work
from dataclasses import asdict

# Import graph schema components
from graph_schema import Diagnosis, Symptom, Target, StimParams, Evidence, SCHEMA_VERSION

# --- Configuration ---
# For local development, replace with your Neo4j credentials and URI
# In a production scenario, these should come from environment variables or a secure config
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "yourStrongPassword") # Use the password you set up

# Hardcoded protocolDatabase (converted from the user's JavaScript)
# NOTE: In a real system, this would come from a file or another data source.
PROTOCOL_DATABASE_PYTHON = {
    'Major Depressive Disorder': {
        'Anhedonia': {
            'target': 'Left DLPFC', 'frequency': '10 Hz', 'intensity': '120% MT', 'pulses': 3000,
            'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'High',
            'notes': 'High-frequency stimulation of left DLPFC shows strong evidence for anhedonia improvement',
            'references': ['George et al., 2010', 'Blumberger et al., 2018']
        },
        'Psychomotor Retardation': {
            'target': 'Left DLPFC + Right DLPFC (sequential)', 'frequency': '10 Hz (L) / 1 Hz (R)',
            'intensity': '120% MT', 'pulses': 3000, 'sessions': '25-36', 'schedule': 'Daily (5x/week)',
            'evidence': 'Moderate-High',
            'notes': 'Bilateral stimulation may be more effective for psychomotor symptoms',
            'references': ["O'Reardon et al., 2007"]
        },
        'Cognitive Impairment': {
            'target': 'Left DLPFC', 'frequency': '20 Hz (iTBS)', 'intensity': '80% AMT', 'pulses': 1800,
            'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'iTBS may provide cognitive benefits with shorter treatment times',
            'references': ['Blumberger et al., 2018']
        }
    },
    'Treatment-Resistant Depression': {
        'Severe Anhedonia': {
            'target': 'Bilateral DLPFC', 'frequency': '10 Hz (L) / 1 Hz (R)', 'intensity': '120% MT',
            'pulses': 4000, 'sessions': '30-36', 'schedule': 'Daily (5x/week) + maintenance',
            'evidence': 'High',
            'notes': 'Extended course with maintenance sessions recommended for TRD'
            # 'references': [] # Assuming none provided for this specific one
        }
    },
    'Obsessive-Compulsive Disorder': {
        'Obsessions': {
            'target': 'Right DLPFC or dACC', 'frequency': '1 Hz (low) or 10 Hz (high)',
            'intensity': '110% MT', 'pulses': 1800, 'sessions': '20-30',
            'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'Both inhibitory and excitatory protocols show promise'
        },
        'Compulsions': {
            'target': 'Pre-SMA or OFC', 'frequency': '1 Hz', 'intensity': '110% MT', 'pulses': 1200,
            'sessions': '25-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'Targeting motor control areas may reduce compulsive behaviors'
        }
    },
    'PTSD': {
        'Intrusive Thoughts': {
            'target': 'Right DLPFC', 'frequency': '1 Hz', 'intensity': '110% MT', 'pulses': 1200,
            'sessions': '20-25', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
            'notes': 'Inhibitory stimulation of right DLPFC may reduce hyperarousal'
        },
        'iTBS Left DLPFC': { # This symptom name might need refinement
            'target': 'Left DLPFC', 'frequency': 'iTBS', 'intensity': '80% AMT', 'pulses': 600,
            'sessions': '20', 'schedule': 'Daily (5x/week)', 'evidence': 'Emerging',
            'notes': 'Intermittent TBS shows promise in PTSD symptom reduction',
            'references': ['Osuch et al., 2009']
        }
    },
    'Schizophrenia (Auditory Hallucinations)': {
        'Auditory Hallucinations': {
            'target': 'Left Temporoparietal Junction', 'frequency': '1 Hz', 'intensity': '90% MT',
            'pulses': 1200, 'sessions': '20-30', 'schedule': 'Daily (5x/week)',
            'evidence': 'Moderate-High',
            'notes': 'Low-frequency stimulation of auditory areas shows good efficacy'
        }
    },
    'Chronic Pain': {
        'Persistent Pain': {
            'target': 'M1 (motor cortex)', 'frequency': '10 Hz', 'intensity': '80-90% MT',
            'pulses': 2000, 'sessions': '15-20', 'schedule': 'Daily (5x/week)',
            'evidence': 'Moderate',
            'notes': 'Motor cortex stimulation for central pain processing'
        }
    },
    'Fibromyalgia': {
        'Widespread Pain': {
            'target': 'M1 (motor cortex)', 'frequency': '10 Hz', 'intensity': '80% MT',
            'pulses': 1600, 'sessions': '20-25', 'schedule': '3-5x/week', 'evidence': 'Moderate',
            'notes': 'Lower intensity may be better tolerated in fibromyalgia patients'
        }
    },
    'Migraine': {
      'Headache Frequency': {
        'target': 'Occipital cortex or M1', 'frequency': '1 Hz or 10 Hz', 'intensity': '90% MT',
        'pulses': 1200, 'sessions': '12-20', 'schedule': '3x/week', 'evidence': 'Moderate',
        'notes': 'Both excitatory and inhibitory protocols show preventive effects'
      }
    },
    'Generalized Anxiety Disorder': {
      'Excessive Worry': {
        'target': 'Left DLPFC', 'frequency': '10 Hz', 'intensity': '110% MT', 'pulses': 2000,
        'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
        'notes': 'Standard high-frequency protocol for GAD'
      },
      'Restlessness': {
        'target': 'Right DLPFC', 'frequency': '1 Hz', 'intensity': '120% MT', 'pulses': 1200,
        'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
        'notes': 'Low-frequency right DLPFC may help restlessness'
      },
      '1 Hz Right DLPFC': { # This symptom name might need refinement
        'target': 'Right DLPFC', 'frequency': '1 Hz', 'intensity': '120% MT', 'pulses': 1200,
        'sessions': '20-30', 'schedule': 'Daily (5x/week)', 'evidence': 'Moderate',
        'notes': 'Low-frequency right DLPFC stimulation reduces anxiety symptoms',
        'references': ['Mantovani et al., 2013']
      }
    }
}


class GraphDAO:
    def __init__(self, driver: Driver):
        self.driver = driver

    @staticmethod
    @unit_of_work(timeout=(5 * 60)) # 5 minute timeout
    def _execute_query(tx: ManagedTransaction, query: str, params: dict = None):
        result = tx.run(query, params or {})
        return [record for record in result]

    def clear_apge_graph(self):
        print("Clearing existing APGE graph data (Diagnosis, Symptom, Target, StimParams, Evidence nodes and their relationships)...")
        # Detach delete to remove nodes and their relationships
        # Matches nodes based on schema_version to only remove APGE data
        queries = [
            "MATCH (n) WHERE n.schema_version IS NOT NULL DETACH DELETE n",
        ]
        with self.driver.session() as session:
            for query in queries:
                session.execute_write(self._execute_query, query)
        print("Graph cleared.")

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


def main():
    print(f"Starting ETL process for APGE graph (Schema Version: {SCHEMA_VERSION}).")
    print(f"Connecting to Neo4j at {NEO4J_URI} as user {NEO4J_USER}.")
    
    driver = None
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("Successfully connected to Neo4j.")
        
        dao = GraphDAO(driver)
        
        # Clear existing graph data before seeding
        dao.clear_apge_graph()
        
        # Process the protocol database
        print("Processing protocol database...")
        dao.process_database(PROTOCOL_DATABASE_PYTHON)
        
        print("ETL process completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        # Consider more specific error handling for auth errors, connection errors etc.
    finally:
        if driver:
            driver.close()
            print("Neo4j connection closed.")

if __name__ == "__main__":
    main()
