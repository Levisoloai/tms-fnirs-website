import os
import sys
import yaml
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Adjust sys.path to include the src directory
# This allows for direct imports of modules within src
# Assumes the script is in 'scripts/' and 'src/' is a sibling directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.apge.etl import GraphDAO
from src.apge.graph_schema import SCHEMA_VERSION, Diagnosis, Symptom, Target, StimParams, Evidence

def main():
    """
    Main function to seed the Neo4j database with protocol data from a YAML file.
    """
    # Construct the absolute path to the .env file
    dotenv_path = os.path.join(project_root, 'src', 'apge', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Attempting to load .env file from: {dotenv_path}")

    NEO4J_URI = os.environ.get("NEO4J_URI")
    NEO4J_USER = os.environ.get("NEO4J_USER")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

    if not NEO4J_URI or not NEO4J_USER:
        print("NEO4J_URI and NEO4J_USER must be set in the environment or .env file.")
        # Fallback to default values if not found, though password check is primary
        NEO4J_URI = NEO4J_URI or "neo4j://localhost:7687" # Default if not set
        NEO4J_USER = NEO4J_USER or "neo4j" # Default if not set
        print(f"Using default URI: {NEO4J_URI}, User: {NEO4J_USER} if not found in .env")


    if NEO4J_PASSWORD is None:
        raise ValueError("NEO4J_PASSWORD not found in environment variables. "
                         "Please set it in the .env file (src/apge/.env) or environment.")

    print(f"Starting seeding process for APGE graph (Schema Version: {SCHEMA_VERSION}).")
    print(f"Connecting to Neo4j at {NEO4J_URI} as user {NEO4J_USER}.")

    # Construct the absolute path to the protocols.yaml file
    protocols_file_path = os.path.join(project_root, 'src', 'apge', 'protocols', 'protocols.yaml')
    print(f"Loading protocol data from: {protocols_file_path}")

    try:
        with open(protocols_file_path, 'r') as file:
            protocol_data_from_yaml = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Protocol file not found at {protocols_file_path}")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return

    if not protocol_data_from_yaml:
        print("No data loaded from YAML file. Exiting.")
        return

    driver = None
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("Successfully connected to Neo4j.")

        dao = GraphDAO(driver)

        # Apply schema constraints before clearing or adding data
        dao.apply_schema_constraints()

        print("Clearing existing APGE graph data...")
        dao.clear_apge_graph()
        print("Graph data cleared.")

        print("Processing and seeding new data from YAML...")
        dao.process_database(protocol_data_from_yaml) # This method is in etl.py

        print("Seeding process completed successfully.")

    except Exception as e:
        print(f"An error occurred during the seeding process: {e}")
        # More specific error handling can be added here (e.g., for auth, connection issues)
    finally:
        if driver:
            driver.close()
            print("Neo4j connection closed.")

if __name__ == "__main__":
    main()
