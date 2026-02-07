# Travel Planner API

Welcome to the Travel Planner repository!

This is a technical test for a Python engineer position. The project is a RESTful API designed for planning art-focused trips, featuring a smooth integration with the **Art Institute of Chicago API**.

I’ve implemented full CRUD functionality, external data validation, automatic project completion logic, and safety checks to prevent accidental deletions.

## 🛠Tech Stack

I chose this specific stack to ensure maximum performance and "set-it-and-forget-it" automatic documentation:

- **Python 3.12.3**
- **FastAPI:** For building a lightning-fast, asynchronous API.
- **SQLAlchemy (SQLite):** For reliable data storage without the headache of setting up a heavy database server.
- \*Pydantic:\*\* For strict data validation (no junk data allowed!).
- **Docker:** To containerize the application so it works perfectly on any machine, no "it works on my computer" excuses.

---

## How to Run (Step-by-Step)

If you're seeing this code for the first time and want to take it for a spin, you have two options: Docker (highly recommended) or running it locally via Python.

### Option 1: Running via Docker(the easy way)

Make sure you have Docker Desktop installed.

1.  **Build the image:**
    First, clone the repository and open the project in your favorite editor(like **VS Code**).

    ```bash
    docker build -t travel-planner .
    ```

2.  **Run the container:**
    `bash
docker run -p 8000:8000 travel-planner
`
    And you're live! Head over to the "How to Test" section.

### Option 2: Local Setup (Python)

If you prefer to run the code directly:

1.  **Clone the repository:**

    ```bash
    git clone <repo-link>
    cd travel_planner
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # For mac/Linux
    # OR
    venv\Scripts\activate     # For windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Launch the server:**
    ```bash
    uvicorn main:app --reload
    ```

---

## How to Test(Interactive Docs)

The coolest feature of this project is the automatic interactive documentation. You don’t even need to open Postman (though it works there too)—you can test everything right in your browser.

1.  Open your browser and go to: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
2.  You’ll see the **Swagger UI**-a clean list of all available commands.

### Smoke Test Scenario

Let’s walk through a typical user journey to see the magic in action:

**Step 1: Create a project with art spots**

- Find the `POST /projects/` block.
- Click **Try it out**.
- Paste this JSON (we're creating a "Chicago Art Trip" and adding Van Gogh’s "The Bedroom", ID 28560):
  ```json
  {
    "name": "Chicago Art Trip",
    "description": "Visiting the best impressionist works",
    "start_date": "2023-10-25",
    "initial_places": [28560]
  }
  ```
- Click **Execute**.
- The response will show your project with `id: 1` and `is_completed: false`. The system automatically fetched the painting's title from the Chicago API for you!

**Step 2: Try adding a non-existent place (Validation Check)**

- Find the `POST /projects/{project_id}/places/` block.
- Enter `project_id`: **1**.
- In the request body, enter an ID that doesn't exist (e.g., 99999999):
  ```json
  {
    "external_id": 99999999,
    "notes": "Must see"
  }
  ```
- You’ll get a **404 error** because the museum doesn't have that ID.

**Step 3: Mark a place as visited**

- First, find the internal ID of the place (not the external_id). Call `GET /projects/1` and look for the `id` in the `places` list (it’s likely 1).
- Go to `PUT /places/{place_id}`.
- Enter `place_id`: **1**.
- Use this JSON:
  ```json
  {
    "visited": true,
    "notes": "The colors are even more amazing in person!"
  }
  ```
- Now, call `GET /projects/1` again. You’ll notice the project status `is_completed` has automatically flipped to **true**.

---

## Project Structure

- `main.py`: The entry point. Houses the API endpoints (The Controller).
- `models.py`: Database table definitions (The DB Models).
- `schemas.py`: Data validation rules (The Pydantic Models).
- `database.py`: SQLite connection settings.

## Note on User Experience (Frontend Integration)

While this repository focuses on the Backend API, here is how the User Flow is designed for the client-side application:

1.  **Search Phase:** The user types an artist name (e.g., "Monet") or artwork title into the search bar.
2.  **Integration:** The Frontend calls the Art Institute public search endpoint (`/api/v1/artworks/search?q=Monet`) to retrieve a list of matching artworks with their internal IDs.
3.  **Selection:** The user selects an artwork from the visual list.
4.  **Backend Call:** The Frontend extracts the `id` from the selected artwork and sends it to our `POST /projects/{id}/places/` endpoint.

_This ensures the user never has to manually deal with numeric IDs, providing a seamless experience._

Thanks for checking out my test task!
