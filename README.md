# Project Overview and Architecture

This project implements a microservice-based application designed to deliver a comprehensive educational resource on Transcranial Magnetic Stimulation (TMS) and Functional Near-Infrared Spectroscopy (fNIRS) integration. It includes an interactive TMS Protocol Tool for exploring potential treatment parameters. The architecture is divided into three main services: `ingest`, `api`, and `web`, each with distinct responsibilities.

## Services

### 1. Ingest Service (`ingest/`)

*   **Role:** This service is responsible for processing raw data sources, such as research literature, clinical guidelines, and other relevant documents. It extracts meaningful information, generates vector embeddings for semantic search capabilities, and populates both a relational database for structured metadata and a vector database for similarity searches.
*   **Key Technologies:** Python scripts, `sentence-transformers` library for creating text embeddings.
*   **Outputs:** Populates an SQLite database (for metadata, structured data) and a FAISS index (for vector embeddings).

### 2. API Service (`api/`)

*   **Role:** This service provides a backend API that serves data to the frontend application. It handles user queries, retrieves information from the SQLite database and FAISS index, and interfaces with an Advanced Protocol Generation Engine (APGE) for the TMS Protocol Tool.
*   **Key Technologies:** FastAPI (Python web framework), SQLite (for structured data), FAISS (for vector similarity search).
*   **Interfaces:** Communicates with the `web/` service (frontend), the SQLite database, the FAISS index, and the APGE.

### 3. Web Service (`web/`)

*   **Role:** This service delivers the user-facing frontend application. It includes the main educational content, the user interface for interacting with the data, and the TMS Protocol Tool which leverages the APGE via the `api/` service.
*   **Key Technologies:** Next.js (React framework), React (JavaScript library for UI), Tailwind CSS (utility-first CSS framework).
*   **Interfaces:** Interacts with users and makes requests to the `api/` service to fetch data and receive protocol suggestions.

## High-Level Data Flow Diagram

The following diagram illustrates the general flow of data and interactions between the services:

```
Raw Data --(Python scripts, sentence-transformers in ingest/)--> SQLite DB (metadata, structured data)
                                                              |
                                                              +--> FAISS Index (vector embeddings)

User <-- (Next.js/React, Tailwind CSS in web/) --> FastAPI Backend (api/) --> APGE (for TMS Protocol Tool)
                                                       |         ^
                                                       |         | (queries, data retrieval)
                                                       +---------+--> SQLite DB & FAISS Index
```

This architecture allows for a modular and scalable system, where each component can be developed, deployed, and maintained independently.

## Quick Start with Docker Compose

This section provides a step-by-step guide to quickly set up and run the entire application stack (ingest, api, web services) using Docker Compose.

### Prerequisites

*   **Docker and Docker Compose:** Ensure you have Docker Desktop (which includes Docker Compose) installed on your system. For installation instructions, see the [official Docker documentation](https://docs.docker.com/get-docker/).

### 1. Clone the Repository

First, clone the project repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/your-username/tms-fnirs-microsite.git # Replace with the actual repository URL
cd tms-fnirs-microsite # Replace with the actual repository name
```

### 2. Configure Environment Variables

Some services, particularly the `api` and `ingest` services, may require API keys or specific path configurations. Create a `.env` file in the root of the project directory by copying the example file if provided, or create one manually:

```bash
# Example: copy .env.example .env
# Then edit .env with your specific values.
```

Add the following environment variables to your `.env` file:

| Environment Variable | Description                                                                 | Default / Example Value          | Required |
|----------------------|-----------------------------------------------------------------------------|----------------------------------|----------|
| `OPENAI_API_KEY`     | API key for OpenAI services (used by the Advanced Protocol Generation Engine - APGE). | `your_openai_api_key_here`       | Yes      |
| `DATABASE_URL`       | Connection string for the SQLite database used by the `api` and `ingest` services. | `sqlite:///./data/app.db`        | No       |
| `FAISS_INDEX_PATH`   | Filesystem path where the FAISS index is stored by `ingest` and read by `api`. | `./data/faiss.index`             | No       |

**Note:**
*   The `DATABASE_URL` and `FAISS_INDEX_PATH` often have sensible defaults in the `docker-compose.yml` or application code, pointing to locations within Docker volumes. Modify them only if you have specific needs for data persistence locations.
*   The `OPENAI_API_KEY` is essential for the TMS Protocol Tool's advanced features.

### 3. Build and Start Services

Once the `.env` file is configured, you can build the Docker images for each service and start the application stack in detached mode (running in the background) using the following command:

```bash
docker compose up -d
```

This command will:
*   Read the `docker-compose.yml` file.
*   Build Docker images for the `ingest`, `api`, and `web` services if they haven't been built already or if their Dockerfiles have changed.
*   Start containers for each service.
*   The `ingest` service will typically run to completion (processing data and populating the database/index) and then exit if designed as a one-off task. The `api` and `web` services will continue running.

You can view the logs for all services (or a specific service) using:
```bash
docker compose logs -f
# docker compose logs -f api # Example for a specific service
```

### 4. Access the Web Application

After the services have started successfully (especially the `web` and `api` services), you can access the web interface. Open your web browser and navigate to:

[http://localhost:3000](http://localhost:3000)

(The port may vary if configured differently in your `docker-compose.yml` for the `web` service).

### 5. Shutting Down Services

To stop and remove all the containers, networks, and volumes defined in your `docker-compose.yml`, run the following command from the project root directory:

```bash
docker compose down
```

If you only want to stop the services without removing them, you can use `docker compose stop`.

## API Reference

The `api` service provides RESTful endpoints for querying the knowledge base and generating TMS protocol recommendations. The base URL for the API (when running locally via Docker Compose) is typically `http://localhost:8000/api` (the port might vary based on Docker Compose configuration).

### 1. Query Knowledge Base

*   **Endpoint**: `GET /api/query`
*   **Description**: Searches the knowledge base using a text query. It leverages the FAISS index for semantic similarity search and retrieves corresponding metadata from the SQLite database.
*   **Request Parameters**:
    *   `q` (string, required): The text query for searching.
    *   `k` (integer, optional, default: 5): The maximum number of results to return.
*   **Example Request**:
    ```bash
    curl "http://localhost:8000/api/query?q=tms+for+depression&k=3"
    ```
*   **Response Structure**:
    A successful request returns a JSON array of search result objects. Each object typically includes:
    *   `id`: A unique identifier for the document or data chunk.
    *   `title`: The title of the source document or a relevant heading.
    *   `text`: The actual text snippet that matched the query.
    *   `source`: Information about the origin of the data (e.g., publication name, section).
    *   `score`: A similarity score indicating relevance (if applicable).
    ```json
    [
      {
        "id": "doc123",
        "title": "TMS for Treatment-Resistant Depression",
        "text": "High-frequency TMS over the left DLPFC has shown efficacy...",
        "source": "Journal of Clinical Psychiatry, 2023",
        "score": 0.89
      },
      {
        "id": "guide002",
        "title": "Clinical Guidelines for Neuromodulation",
        "text": "When considering TMS for depression, patient history and symptom severity are key.",
        "source": "NeuroModulation Society Guidelines, 2024",
        "score": 0.85
      }
    ]
    ```
*   **Common HTTP Status Codes**:
    *   `200 OK`: Successful request. Results are in the response body.
    *   `400 Bad Request`: Invalid parameters (e.g., missing `q`, `k` not an integer).
    *   `500 Internal Server Error`: Server-side error during query processing.

### 2. Get TMS Protocol Recommendation

*   **Endpoint**: `POST /api/protocol/recommend`
*   **Description**: Receives patient and clinical data as a JSON object and returns personalized TMS protocol recommendations generated by the Advanced Protocol-Generation Engine (APGE).
*   **Request Body**:
    A JSON object containing patient and clinical information. Key fields include:
    ```json
    {
      "diagnosis": "Major Depressive Disorder",
      "symptoms": ["Anhedonia", "Cognitive Impairment"],
      "severity": "Severe",
      "age": 45,
      "medicationResistant": true,
      "previousTreatments": ["SSRI", "SNRI"],
      "comorbidities": ["Anxiety Disorder"],
      "contraindications": []
    }
    ```
    *(Refer to the input fields of the TMS Protocol Tool, as implemented in the `web/` service, for a comprehensive list of possible parameters.)*
*   **Example Request**:
    ```bash
    curl -X POST http://localhost:8000/api/protocol/recommend \
         -H "Content-Type: application/json" \
         -d '{
               "diagnosis": "Major Depressive Disorder",
               "symptoms": ["Anhedonia"],
               "severity": "Moderate",
               "age": 35
             }'
    ```
*   **Response Structure**:
    A successful request returns a JSON object detailing the recommended protocol(s) and related considerations.
    ```json
    {
      "primaryProtocol": {
        "target": "Left DLPFC",
        "frequency": "10 Hz",
        "intensity": "120% MT",
        "pulsesPerSession": 3000,
        "totalSessions": "20-30",
        "schedule": "Daily (5x/week)",
        "evidenceLevel": "High",
        "notes": "Standard high-frequency protocol for MDD, particularly effective for anhedonia."
      },
      "alternativeProtocols": [
        {
          "target": "Right DLPFC",
          "frequency": "1 Hz (iTBS)",
          "intensity": "110% MT",
          "pulsesPerSession": 600,
          "totalSessions": "20",
          "schedule": "Daily (5x/week)",
          "evidenceLevel": "Moderate",
          "notes": "Consider if anxiety is a prominent comorbidity or if patient prefers shorter sessions."
        }
      ],
      "safetyConsiderations": [
        "Assess motor threshold accurately.",
        "Monitor for potential side effects like headache or scalp discomfort.",
        "Screen for mood changes, including hypomania/mania risk, especially if bipolar features are suspected."
      ],
      "monitoringPlan": [
        "Weekly symptom rating scales (e.g., PHQ-9, BDI).",
        "Motor threshold reassessment every 5-10 sessions or if coil position changes."
      ],
      "expectedOutcomes": {
        "timeline": "Initial response typically seen at 2-3 weeks.",
        "responseRate": "Approximately 50-60% for MDD.",
        "peakResponse": "4-6 weeks post-treatment initiation."
      },
      "apgeVersion": "1.0.2"
    }
    ```
*   **Common HTTP Status Codes**:
    *   `200 OK`: Successful request. Recommendation is in the response body.
    *   `422 Unprocessable Entity`: Invalid request body (e.g., missing required fields like `diagnosis` or `symptoms`, incorrect data types). The response body may contain details about the validation errors.
    *   `500 Internal Server Error`: Server-side error, which could indicate a problem with the APGE or other internal processes.
*   `503 Service Unavailable`: The APGE or a critical downstream service might be temporarily unavailable.

### 3. List Available Protocols

*   **Endpoint**: `GET /api/protocol/list`
*   **Description**: Returns a simplified list of protocols that can be selected for comparison. Optionally filter by diagnosis.
*   **Request Parameters**:
    *   `diagnosis` (string, optional): Filter protocols linked to a specific diagnosis.
*   **Example Request**:
    ```bash
    curl "http://localhost:8000/api/protocol/list?diagnosis=MDD-anxious"
    ```
*   **Response Structure**:
    An array of protocol summaries:
    ```json
    [
      { "id": "p1", "label": "Left DLPFC 10Hz", "device": "MagStim", "evidence_level": "High" }
    ]
    ```

### 4. Compare Protocols

*   **Endpoint**: `POST /api/protocol/compare`
*   **Description**: Accepts a list of protocol IDs and returns a comparison table plus a short narrative summary.
*   **Request Body**:
    ```json
    { "ids": ["p1", "p2", "p3"] }
    ```
*   **Example Request**:
    ```bash
    curl -X POST http://localhost:8000/api/protocol/compare \
         -H "Content-Type: application/json" \
         -d '{"ids": ["p1","p2"]}'
    ```
*   **Response Structure**:
    ```json
    {
      "table": { "columns": ["Protocol Name", "Coil Type", "Frequency"], "data": [["Left DLPFC 10Hz", "Figure-8", "10 Hz"]] },
      "narrative_md": "Markdown summary..."
    }
    ```

## TMS Protocol Tool and Advanced Protocol-Generation Engine (APGE)

This section details the interactive TMS Protocol Tool available to users and the underlying engine that powers its recommendations.

### TMS Protocol Tool

The TMS Protocol Tool serves as the primary user interface for accessing the system's TMS protocol generation capabilities. It is an integral part of the `web/` service and is built using Next.js and React.

When a user inputs clinical and patient-specific data into the tool, it constructs a request and sends it to the `/api/protocol/recommend` endpoint provided by the `api/` service. The tool then receives and presents the generated protocol recommendations in a structured, user-friendly format.

### Protocol Comparator

In addition to generating individual recommendations, the frontend includes a **Protocol Comparator** page. Users can choose up to four protocols from the list endpoint and view them side by side. The table supports sorting and filtering, produces a short narrative summary, and can be exported to PDF. Permalink URLs encode the selected protocol IDs so comparisons can be easily shared.

### Advanced Protocol-Generation Engine (APGE)

The Advanced Protocol-Generation Engine (APGE) is the core logic responsible for generating personalized TMS protocol recommendations. It operates as a distinct component, invoked by the `api/` service when a request to the `/api/protocol/recommend` endpoint is received.

**Purpose:** The APGE's primary purpose is to synthesize clinical input data (such as diagnosis, symptoms, patient history) with evidence derived from the project's knowledge base (literature, guidelines stored in SQLite and FAISS) to suggest appropriate TMS treatment parameters.

**Algorithmic Approach:** At a high level, the APGE employs a sophisticated approach to derive its recommendations. This involves analyzing the input parameters and cross-referencing them with the indexed literature and clinical data. It may leverage techniques such as natural language processing (NLP) to understand textual information from the knowledge base and a system of rule-based heuristics or a machine learning model trained on existing protocol data to refine and personalize the suggestions. The engine aims to balance evidence-based practices with individual patient characteristics.

**Further Details:** For a more detailed technical description of the APGE, including its architecture, data processing pipelines, and decision-making algorithms, please see the [APGE Design Document](docs/apge_design.md). (Design document coming soon if link is broken.)

## Tech Stack

This section outlines the primary technologies and frameworks used across the different services of the TMS-fNIRS Microsite.

### Core Technologies

*   **Backend (`api/` service):**
    *   **Framework:** FastAPI (Python)
    *   **Data Storage:** SQLite (for structured metadata)
    *   **Vector Search:** FAISS (for similarity search on embeddings)
    *   **Embeddings:** `sentence-transformers` (Python library for generating text embeddings, utilized by both `ingest/` and potentially `api/` for query processing)

*   **Frontend (`web/` service):**
    *   **Framework:** Next.js (React framework)
    *   **UI Library:** React 18
    *   **Styling:** Tailwind CSS

*   **Data Ingestion (`ingest/` service):**
    *   **Scripting:** Python
    *   **Embeddings:** `sentence-transformers` (for processing raw data and generating embeddings)

*   **General / DevOps:**
    *   **Containerization:** Docker and Docker Compose

### Legacy Version Note

A legacy version of the TMS Protocol Tool, built with HTML, Vanilla JavaScript, and standalone Babel for in-browser React rendering, can be found at `tms_protocol_tool.html`. This version might offer a simplified, standalone example of the tool's core logic. However, active development and the full feature set, including APGE integration, are focused on the Next.js application within the `web/` directory.

### Frontend Development Details

For detailed front-end development instructions specific to the `web/` service (including component structure, state management, and specific build/test commands), please refer to the `web/README.md` file.

## Regulatory Disclaimer and Data Handling

This section provides crucial information regarding the intended use of this project and responsibilities concerning data handling.

### Regulatory Disclaimer

**This project is a prototype intended for research and educational purposes only. It is NOT an FDA-cleared medical device and should NOT be used for clinical decision-making, diagnosis, or treatment.**

Any information, suggestions, or outputs generated by this system, including the TMS Protocol Tool and the Advanced Protocol-Generation Engine (APGE), are for informational exploration and academic research. They are not a substitute for professional medical advice, diagnosis, or treatment provided by qualified healthcare professionals. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read or interpreted from this project.

### Data Handling Practices

The system is designed to work with anonymized or synthetic data for development and research. If handling any potentially sensitive information, users are responsible for ensuring compliance with all applicable data privacy regulations, such as HIPAA (in the United States) and GDPR (in Europe).

The project developers strongly recommend following best practices for data minimization, anonymization, and secure storage when using or adapting this system.

**Note on Local Data Storage:** The provided Docker Compose setup, by default, stores data such as the SQLite database and FAISS index in local Docker volumes on the host machine. Users are responsible for managing these volumes appropriately, especially if any sensitive or potentially identifiable data is processed or stored during local development or testing. Ensure that access to these local volumes is secured according to your institution's data security policies and relevant regulations.

## Quality Assurance and Contributing

We welcome contributions to enhance this project! To maintain a high standard of quality and consistency, we utilize several tools and a defined process for contributions. Adhering to these guidelines helps streamline the review process.

### Quality Assurance (QA)

Before submitting any changes, please ensure your contributions meet our quality standards by running the relevant checks for the services you've modified.

#### Back-end (Python/FastAPI)

For the `api/` and `ingest/` services, which are Python-based, please run the following commands from their respective service directories (e.g., `cd api/`):

*   **Run Tests (pytest):**
    ```bash
    pytest
    ```
*   **Test Coverage (coverage.py):**
    ```bash
    coverage run -m pytest && coverage report -m
    ```
    *(Note: This may also generate a `coverage.xml` file, which can be used by CI systems.)*
*   **Code Formatting (Black):**
    ```bash
    black . --check
    ```
*   **Linting (Ruff):**
    ```bash
    ruff .
    ```

Ensure all these checks pass with no errors before submitting your contribution.

#### Front-end (Next.js/React)

For front-end specific linting (e.g., ESLint), formatting (e.g., Prettier), and testing (e.g., Jest, React Testing Library) related to the `web/` service, please refer to the detailed instructions and scripts available in the `web/README.md` file.

### Contributing Guidelines

Contributions are welcome! Please follow this general workflow:

1.  Fork the repository and create a feature branch from `main` (or `develop` if that's the project's convention).
2.  Make your changes, adhering to the coding standards and QA guidelines for the respective service (backend/frontend).
3.  Ensure all relevant tests pass and QA checks are clean for the components you have modified.
4.  If adding new features, changing API contracts, or modifying core behavior, please update relevant documentation (this README, API documentation, design documents like `docs/apge_design.md`, or service-specific READMEs).
5.  Submit a Pull Request (PR) to the appropriate branch with a clear description of your changes and link to any relevant issues.

For more specific setup, development, or contribution details related to a particular service, please refer to the `README.md` file within that service's directory (e.g., `api/README.md`, `web/README.md`, `ingest/README.md`) if they exist.

## Image Attributions

All images used in this microsite are believed to be from open-access sources, public domain, or used with appropriate permissions. Detailed information regarding the source and license for each image can be found in the [`images/image_attributions.md`](images/image_attributions.md) file.

We have made every effort to ensure proper attribution. If you find any discrepancies or have concerns about image usage, please open an issue in the repository.

## License

This project is licensed under the MIT License. This means you are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions outlined in the license.

For the full terms and conditions, please see the [LICENSE](./LICENSE) file in the root directory of this project.
