# APGE Development Setup: Neo4j

This document outlines how to set up a Neo4j Community Edition database using Docker for local development of the Advanced Protocol-Generation Engine (APGE).

## Running Neo4j with Docker

To start a Neo4j container, run the following command in your terminal:

```bash
docker run --rm -d \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/yourStrongPassword \
  --name apge-neo4j \
  neo4j:5.20-community
```

**Explanation:**
*   `docker run`: Command to run a Docker container.
*   `--rm`: Automatically removes the container when it stops. For persistent data during development, you might consider mounting a volume (see Neo4j Docker documentation).
*   `-d`: Runs the container in detached mode (in the background).
*   `-p 7474:7474`: Maps port 7474 on your local machine to port 7474 in the container. This is for the Neo4j Browser interface.
*   `-p 7687:7687`: Maps port 7687 on your local machine to port 7687 in the container. This is for the Bolt protocol, used by Neo4j drivers (e.g., from Python).
*   `-e NEO4J_AUTH=neo4j/yourStrongPassword`: Sets the initial username to `neo4j` and the password to `yourStrongPassword`. **IMPORTANT: Change this default password immediately after your first login to the Neo4j Browser.**
*   `--name apge-neo4j`: Assigns a recognizable name to the container, making it easier to manage (e.g., `docker stop apge-neo4j`).
*   `neo4j:5.20-community`: Specifies the official Neo4j Community Edition image, version 5.20.

## Accessing Neo4j

*   **Neo4j Browser:**
    *   Open your web browser and navigate to `http://localhost:7474`.
    *   Log in using the username `neo4j` and the password you set (initially `yourStrongPassword`).
    *   You will be prompted to change the password upon first login.
*   **Python Driver Connection:**
    *   **URI**: `neo4j://localhost:7687` (or `bolt://localhost:7687`)
    *   **Username**: `neo4j`
    *   **Password**: The password you set after the initial change.

## Stopping the Container

To stop the Neo4j container:

```bash
docker stop apge-neo4j
```

If you didn't use `--rm`, to start it again:
```bash
docker start apge-neo4j
```

## Data Persistence (Optional for Deeper Development)

If you want your data to persist beyond the life of a single container run (i.e., not use `--rm` or ensure data is saved if you do use `--rm` and `docker stop`), you should mount a volume. For example:

```bash
docker run -d \
  -p 7474:7474 -p 7687:7687 \
  -v $PWD/neo4j-data:/data \
  -e NEO4J_AUTH=neo4j/yourStrongPassword \
  --name apge-neo4j-persistent \
  neo4j:5.20-community
```
This mounts a `neo4j-data` directory from your current working directory into the container's `/data` directory.

## Seeding the Database

Once Neo4j is running (as described above), you can seed it with initial data using the `scripts/seed.py` script. This script will clear any existing APGE-related data (nodes with a `schema_version` property) and then load the protocols defined in `src/apge/protocols/protocols.yaml`.

**Steps to seed the database:**

1.  **Ensure Neo4j is Running:** Follow the Docker instructions in the "Running Neo4j with Docker" section.
2.  **Set up Environment Variables:**
    Create a `.env` file in the `src/apge/` directory (i.e., `src/apge/.env`). This file should contain your Neo4j connection details:
    ```env
    NEO4J_URI=neo4j://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=yourStrongPassword # Use the password you set for Neo4j
    # NEO4J_DELETABLE_LABELS=Diagnosis,Symptom,Target,StimParams,Evidence
    ```
    Replace `yourStrongPassword` with the actual password you configured for your Neo4j instance.

    The `.env` file also supports an optional variable:
    *   `NEO4J_DELETABLE_LABELS`:
        *   **Purpose**: To specify which Neo4j node labels should be deleted when the database is cleared by the seed script (`scripts/seed.py` via `GraphDAO.clear_apge_graph()`).
        *   **Format**: A comma-separated string of Neo4j labels (e.g., `Diagnosis,Symptom,Target`).
        *   **Default Behavior**: If not set or empty, the seed script defaults to deleting nodes with the labels: `Diagnosis`, `Symptom`, `Target`, `StimParams`, and `Evidence`.
        *   **Example**: `NEO4J_DELETABLE_LABELS=Diagnosis,Symptom,CustomLabel`
        *   **Safety Note**: Use with caution. If you have other data in your Neo4j instance that uses these labels, it will also be deleted. For APGE development, the default usually targets only APGE-managed data.

3.  **Install Dependencies:**
    Make sure you have the necessary Python packages installed. From the project root directory, run:
    ```bash
    pip install -r src/apge/requirements.txt
    ```
4.  **Run the Seeding Script:**
    From the project root directory, execute the script:
    ```bash
    python scripts/seed.py
    ```
    You should see output indicating the connection progress, data clearing, processing, and a success message upon completion. If there are errors (e.g., connection issues, missing `.env` file, incorrect password), they will be printed to the console.
    The seed script also ensures that uniqueness constraints are applied to the database schema for relevant node types and properties.

## Running the API Server (FastAPI)

The APGE project includes a FastAPI server to expose various endpoints. Currently, it provides an endpoint to retrieve the treatment protocols.

**Steps to run the API server:**

1.  **Prerequisites:**
    *   **Neo4j Running (Optional for some endpoints):** While the current `/protocols` endpoint does not directly query Neo4j, future endpoints likely will. Ensure Neo4j is running as described in "Running Neo4j with Docker" if you plan to use or develop database-dependent endpoints.
    *   **Environment Variables (`.env`):** Similarly, ensure your `src/apge/.env` file is configured with database credentials, as this will be needed for database interactions.
    *   **Install Dependencies:** Make sure all Python packages, including `fastapi` and `uvicorn`, are installed. From the project root directory:
        ```bash
        pip install -r src/apge/requirements.txt
        ```

2.  **Start the Uvicorn Server:**
    To run the FastAPI application, use Uvicorn. From the project root directory, execute:
    ```bash
    uvicorn src.apge.api.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `src.apge.api.main:app`: Points to the FastAPI application instance (`app`) in your `main.py` file.
    *   `--reload`: Enables auto-reloading for development. Uvicorn will watch for code changes and automatically restart the server.
    *   `--host 0.0.0.0`: Makes the server accessible from your local network (not just `localhost`).
    *   `--port 8000`: Specifies the port on which the server will listen.

3.  **Accessing the API:**
    *   The API will be available at `http://localhost:8000`.
    *   The `/protocols` endpoint can be accessed at `http://localhost:8000/protocols`.

4.  **API Documentation:**
    FastAPI automatically generates interactive API documentation:
    *   **Swagger UI:** `http://localhost:8000/docs`
    *   **ReDoc:** `http://localhost:8000/redoc`
    You can use these interfaces to explore and test the API endpoints.
