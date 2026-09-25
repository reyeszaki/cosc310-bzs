# BZS — Food Delivery App

Team BZS’s food-delivery project for COSC 310.

For Milestone 0, we are building the backend foundation: a running API, restaurant data stored in JSON, and automated tests. The frontend and authentication will be added in later milestones.

## Requirements

- Python 3.14.0
- Git
- Packages listed in `requirements.txt`

## Setup

Clone the repository and open the project folder:

```bash
git clone https://github.com/reyeszaki/cosc310-bzs.git
cd cosc310-bzs
```

### Create a virtual environment

Use the Python version listed above.

For macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Check the version inside the environment:

```bash
python --version
```

### Install dependencies

With the virtual environment active, run:

```bash
python -m pip install -r requirements.txt
```

Each team member creates their own virtual environment. The `.venv` folder should not be committed to GitHub.

## Running the App

From the project root, with the virtual environment active, run:

```bash
python -m uvicorn main:app --reload
```

[Confirm that `main.py` defines the FastAPI instance as `app` before using this command.]

The server runs at:

http://127.0.0.1:8000

The interactive API documentation is available at:

http://127.0.0.1:8000/docs

Keep the terminal open while using the app. Press `Ctrl+C` to stop the server.

## API Endpoints

The following endpoints are required for M0. Confirm the paths against the completed app.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Check that the app is running. Returns HTTP 200. |
| GET | `/restaurants` | Return the restaurant list. |
| GET | `/docs` | Open the interactive API documentation. |

## Backend Structure

The restaurant-list operation follows:

**Route → Service → Repository → JSON**

- **Route:** Handles the HTTP request and response.
- **Service:** Handles application logic.
- **Repository:** Reads the stored restaurant data.
- **JSON file:** Stores the restaurant records.

The route should not read the JSON file directly. The restaurant schema defines the fields and data types using Pydantic and should be used as the endpoint’s response model.

## Restaurant Data

The restaurant data file is located at:

```text
data/restaurents.json
```

The filename above matches its current spelling in the project.

For M0, the file must contain at least two restaurants with stable IDs and fields that match the restaurant schema.

### Data Configuration

[Add the configuration setting or function argument used to select the data file, its default value, and how to change it.]

The application and tests must support different data locations without relying on machine-specific paths.

## Testing

Automated tests are still being added.

Once the pytest suite is available, run it from the project root:

```bash
python -m pytest
```

The required tests cover:

- The health endpoint.
- The restaurant-list operation.
- Restaurant repository behaviour.
- At least one meaningful invalid or failure case.

Tests must use temporary or isolated data and must not modify the committed restaurant data.

[Update this section when the tests are complete and describe the failure case covered.]

## Project Structure

| Path | Purpose |
| --- | --- |
| `main.py` | Application entry point. |
| `app/api/routers/restaurant_routers.py` | Restaurant API routes. |
| `app/services/restaurant_service.py` | Restaurant application logic. |
| `app/repository/restaurant_repo.py` | Access to stored restaurant data. |
| `app/schema/restaurant_schema.py` | Restaurant data model. |
| `data/restaurents.json` | Restaurant records. |
| `scrum/team-agreement.md` | Versioned team agreement. |
| `requirements.txt` | Python dependencies. |
| `.gitignore` | Files excluded from Git. |
| `README.md` | Setup and usage instructions. |

## Team Agreement

The team agreement is stored in:

```text
scrum/team-agreement.md
```

It includes a version number and is reviewed each week. Changes must be agreed to by everyone on the team.

## M0 Submission

The final M0 version will be tagged `foundation-gate` after the required work has been merged and checked.

The submitted tag identifies the version used for assessment. It must not be moved or overwritten after the deadline.

//AI-Assisted