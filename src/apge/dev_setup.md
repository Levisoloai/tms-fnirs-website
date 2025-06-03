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
    ```
    Replace `yourStrongPassword` with the actual password you configured for your Neo4j instance.
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
