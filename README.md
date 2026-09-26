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
git clone [https://github.com/reyeszaki/cosc310-bzs.git](https://github.com/reyeszaki/cosc310-bzs.git)
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
.\.venv\Scripts\Activate.ps1
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
python -m uvicorn app.main:app --reload
```

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
data/restaurants.json
```

For M0, the file must contain at least two restaurants with stable IDs and fields that match the restaurant schema.

### Data Configuration

Restaurant data is stored in `data/restaurants.json` by default. The repository resolves this path relative to its source file, so it works regardless of where the terminal is opened.

To use a different data file, pass its path when creating the repository:

```python
repository = RestaurantRepository(data_path="path/to/restaurants.json")
```

Tests can pass a temporary data file through this argument to keep test data separate from the committed restaurant data.

## Testing

Automated tests are implemented using `pytest` and can be run from the project root:

```bash
python -m pytest
```

The required tests cover:

- The health endpoint returning a 200 OK.
- The restaurant-list operation returning valid Pydantic models.
- Restaurant repository behavior using `tmp_path` to read isolated JSON data without modifying the committed repository data.
- A 404 Not Found failure case for an invalid endpoint URL.

## Project Structure

| Path | Purpose |
| --- | --- |
| `app/main.py` | Application entry point. |
| `app/api/routers/restaurant_routers.py` | Restaurant API routes. |
| `app/services/restaurant_service.py` | Restaurant application logic. |
| `app/repository/restaurant_repo.py` | Access to stored restaurant data. |
| `app/schema/restaurant_schema.py` | Restaurant data model. |
| `data/restaurants.json` | Restaurant records. |
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