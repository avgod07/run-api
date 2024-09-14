# Workout Tracker API

The Workout Tracker API is designed to help users log their workouts, track calories burned, and retrieve recipe suggestions based on workout data. The API integrates user authentication, workout logging, weekly and monthly workout summaries, and interacts with the Spoonacular API to recommend recipes based on calories burned.

## Features

- **User Registration & Authentication**: Secure user management with login and logout functionalities.
- **Workout Tracking**: Log workouts with details like duration, distance, heart rate, and route.
- **Calorie Calculation**: Automatically calculate calories burned based on user weight and workout data.
- **Weekly & Monthly Stats**: Get summarized stats on workouts for the week or month.
- **Recipe Suggestions**: Retrieve recipe suggestions based on calories burned using Spoonacular API.

## Big Picture Design Decisions

1. **Database Choice (SQLite)**: SQLite is used as a lightweight, file-based database for simplicity during development and testing. This choice allows for quick setup and easy portability but could be replaced with more robust databases (e.g., PostgreSQL or MySQL) for production use. Used SQLAlchemy(ORM) to interact with the database.

2. **RESTful Endpoints**: The API follows REST principles to ensure clear communication patterns between the client and server. This ensures scalability and compatibility with a variety of frontend and mobile applications.

3. **User Authentication**: Flask-Login is utilized to manage user sessions securely. This ensures that sensitive operations, such as adding workouts or fetching personalized stats, are only accessible to authenticated users.

4. **Calorie Calculation Logic**: Calories burned are calculated dynamically based on user-specific factors (e.g., weight) and workout data (e.g., distance). This provides a more personalized experience for users and aligns closely with fitness tracking goals.

5. **External API Integration**: The integration with Spoonacular API enhances the workout experience by providing users with personalized recipe suggestions based on their activity. This functionality leverages external APIs to enrich user data and provides a practical use case for workout data beyond mere tracking.

6. ## Endpoints

### 1. `POST /register`

This endpoint allows a new user to register.

**Request:**
- Method: POST
- Endpoint: `/register`
- Body: JSON payload with user data including `username`, `password`, `age`, and `weight`.

**Response:**
- **201 Created**: JSON response confirming successful registration.
- **400 Bad Request**: JSON error message if the username already exists or required fields are missing.

---

### 2. `POST /login`

This endpoint allows an existing user to log in.

**Request:**
- Method: POST
- Endpoint: `/login`
- Body: JSON payload with `username` and `password`.

**Response:**
- **200 OK**: JSON response confirming successful login.
- **400 Bad Request**: JSON error message if the credentials are invalid.

---

### 3. `POST /logout`

This endpoint logs out the current user.

**Request:**
- Method: POST
- Endpoint: `/logout`

**Response:**
- **200 OK**: JSON response confirming successful logout.

---

### 4. `POST /workouts`

This endpoint allows the logged-in user to add a new workout.

**Request:**
- Method: POST
- Endpoint: `/workouts`
- Body: JSON payload with workout data including `duration_minutes`, `distance_km`, `route_nickname`, `heart_rate`.

**Response:**
- **201 Created**: JSON response with the details of the added workout.
- **401 Unauthorized**: JSON error message if the user is not logged in.

---

### 5. `GET /listed_workouts`

This endpoint retrieves all workouts for the logged-in user, with optional date filtering.

**Request:**
- Method: GET
- Endpoint: `/listed_workouts`
- Query Parameters (optional):
  - `start_date`: Filter workouts from this start date (`YYYY-MM-DD`).
  - `end_date`: Filter workouts up to this end date (`YYYY-MM-DD`).

**Response:**
- **200 OK**: JSON response with a list of the user's workouts.
- **401 Unauthorized**: JSON error message if the user is not logged in.

---

### 6. `GET /stats/week`

This endpoint returns workout statistics for the current week for the logged-in user.

**Request:**
- Method: GET
- Endpoint: `/stats/week`

**Response:**
- **200 OK**: JSON response with statistics including total distance, average duration, and total calories burned for the week.
- **401 Unauthorized**: JSON error message if the user is not logged in.

---

### 7. `GET /stats/month`

This endpoint returns workout statistics for the current month for the logged-in user.

**Request:**
- Method: GET
- Endpoint: `/stats/month`

**Response:**
- **200 OK**: JSON response with statistics including total distance, average duration, and total calories burned for the month.
- **401 Unauthorized**: JSON error message if the user is not logged in.

---

### 8. `GET /recipes`

This endpoint fetches recipe suggestions based on calories burned in the user's last workout.

**Request:**
- Method: GET
- Endpoint: `/recipes`


## Testing Endpoints with Postman

This guide walks you through how to test the Workout Tracking API endpoints using Postman.

### Prerequisites:
1. Ensure the Flask application is running locally.
2. Have Postman installed on your computer.

---

### Step 1: Register a User

- **Endpoint**: `/register`
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/register`
- **Body**: 
    - Select "raw" and "JSON" format in Postman.
    ```json
    {
        "username": "testuser",
        "password": "password123",
        "age": 25,
        "weight": 154
    }
    ```

- **Expected Response**:
    - Status: `201 Created`
    - Body:
    ```json
    {
        "message": "User registered successfully!"
    }
    ```

---

### Step 2: Log in a User

- **Endpoint**: `/login`
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/login`
- **Body**: 
    - Select "raw" and "JSON" format in Postman.
    ```json
    {
        "username": "testuser",
        "password": "password123"
    }
    ```

- **Expected Response**:
    - Status: `200 OK`
    - Body:
    ```json
    {
        "message": "Login successful!"
    }
    ```

---

### Step 3: Add a Workout

- **Endpoint**: `/workouts`
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/workouts`
- **Authorization**: 
    - In Postman, go to the "Authorization" tab, and select "Cookies" (automatically handled if you've logged in).
- **Body**: 
    - Select "raw" and "JSON" format in Postman.
    ```json
    {
        "duration_minutes": 30,
        "distance_km": 5.0,
        "route_nickname": "Morning Run",
        "heart_rate": 140
    }
    ```

- **Expected Response**:
    - Status: `201 Created`
    - Body:
    ```json
    {
        "message": "Workout added successfully!"
    }
    ```

---

### Step 4: Get Listed Workouts

- **Endpoint**: `/listed_workouts`
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/listed_workouts`
- **Authorization**: 
    - In Postman, go to the "Authorization" tab, and select "Cookies".
- **Parameters**:
    - Optional Query Parameters (for filtering by date):
        - `start_date` (format: `YYYY-MM-DD`)
        - `end_date` (format: `YYYY-MM-DD`)

- **Expected Response**:
    - Status: `200 OK`
    - Body:
    ```json
    [
        {
            "id": 1,
            "duration_minutes": 30,
            "distance_km": 5.0,
            "route_nickname": "Morning Run",
            "heart_rate": 140,
            "age": 25,
            "weight": 70.5,
            "date_time": "2023-09-14 12:00:00",
            "calories_burned": 262.5
        }
    ]
    ```

---

### Step 5: Fetch Weekly Stats

- **Endpoint**: `/stats/week`
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/stats/week`
- **Authorization**: 
    - In Postman, go to the "Authorization" tab, and select "Cookies".

- **Expected Response**:
    - Status: `200 OK`
    - Body:
    ```json
    {
        "total_distance_week": 5.0,
        "avg_run_duration": 30.0,
        "total_calories_week": 262.5
    }
    ```

---

### Step 6: Fetch Recipes Based on Calories Burned

- **Endpoint**: `/recipes`
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/recipes`
- **Authorization**: 
    - In Postman, go to the "Authorization" tab, and select "Cookies".

- **Expected Response**:
    - Status: `200 OK`
    - Body:
    ```json
    {
        "calories_burned": 262.5,
        "recipes": [
            {
                "title": "Grilled Chicken Salad",
                "calories": 260,
                "image": "https://spoonacular.com/recipeImages/123456-312x231.jpg"
            },
            {
                "title": "Vegetable Stir-fry",
                "calories": 270,
                "image": "https://spoonacular.com/recipeImages/789012-312x231.jpg"
            }
        ]
    }
    ```

---

### Step 7: Log out the User

- **Endpoint**: `/logout`
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/logout`
- **Authorization**: 
    - In Postman, go to the "Authorization" tab, and select "Cookies".

- **Expected Response**:
    - Status: `200 OK`
    - Body:
    ```json
    {
        "message": "Logout successful!"
    }
    ```

**Response:**
- **200 OK**: JSON response with calories burned and recipe suggestions from Spoonacular API.
- **404 Not Found**: JSON error message if no workout data is found for the user.
- **401 Unauthorized**: JSON error message if the user is not logged in.

### Conclusion
By following these steps, you can easily test the Workout Tracking API endpoints using Postman. Ensure to register, log in, and use proper authentication when accessing secured routes like adding workouts or fetching stats. This guide provides a quick and effective way to verify the API's functionality.

---
