# SafeYatra Backend

**FastAPI backend for SafeYatra — an AI-powered tourist safety monitoring and tracking system.**

The SafeYatra backend provides REST APIs for location-based safety assessment, crime-risk prediction, tourist incident reporting, emergency alerts, user data management, and communication between the Flutter mobile application and the machine learning system.

## Overview

SafeYatra uses district-level historical crime statistics from the **National Crime Records Bureau (NCRB)** to estimate tourist safety levels across different regions of India.

The FastAPI backend acts as the central layer connecting the Flutter application, MongoDB database, machine learning model, mapping services, and emergency notification system.

```text
Flutter Mobile App
        │
        ▼
   FastAPI Backend
        │
   ┌────┼───────────────┐
   ▼    ▼               ▼
MongoDB  ML Model   External APIs
         │           ├── Google Maps
         │           ├── Geocoding
         │           └── Firebase
         │
         ▼
   Safety Risk Level
```

## Key Responsibilities

* **Safety Risk Prediction** — Uses the trained Random Forest classifier to classify districts as Safe, Moderate, or High Risk.
* **Crime Data Management** — Stores and retrieves processed NCRB crime profiles.
* **Location Processing** — Receives GPS-resolved district information from the Flutter application.
* **Incident Reporting** — Handles tourist reports including theft, harassment, scams, accidents, and medical emergencies.
* **Emergency System** — Processes SOS requests and coordinates emergency notifications.
* **Geofencing Support** — Provides APIs for restricted and hazardous zone information.
* **Tourist Tracking** — Handles location updates for real-time monitoring.
* **Safety Recommendations** — Provides risk-aware information that can be used for route and destination recommendations.
* **Authority Dashboard APIs** — Supplies tourist locations, incidents, and safety information for monitoring.

## Machine Learning

The backend integrates a **Random Forest classifier** trained using aggregated district-level NCRB crime statistics.

The crime data is processed into categories such as:

* Violent Crime
* Crimes Against Women
* Property Crime
* Fraud / Cybercrime
* Kidnapping
* Other relevant crime indicators

The model predicts a district-level safety category:

```text
Crime Statistics
       │
       ▼
Data Preprocessing
       │
       ▼
Crime Feature Aggregation
       │
       ▼
Random Forest Classifier
       │
       ▼
┌──────────┬──────────┬──────────┐
│   SAFE   │ MODERATE │   HIGH   │
└──────────┴──────────┴──────────┘
```

The prediction is returned to the Flutter application and displayed as part of the tourist safety interface.

## Tech Stack

| Component         | Technology                       |
| ----------------- | -------------------------------- |
| Framework         | FastAPI                          |
| Language          | Python                           |
| Database          | MongoDB                          |
| Machine Learning  | Scikit-learn                     |
| ML Model          | Random Forest                    |
| Data Processing   | Pandas, NumPy                    |
| API Documentation | Swagger / OpenAPI                |
| Authentication    | JWT / Token-based authentication |
| Maps              | Google Maps / Geocoding API      |
| Notifications     | Firebase Cloud Messaging         |
| Frontend          | Flutter                          |
| Data Source       | NCRB crime statistics            |



*The structure can be adjusted according to the actual implementation.*

## API Flow

### Safety Prediction

```text
Flutter App
    │
    │ District / Location
    ▼
FastAPI
    │
    ▼
Retrieve Crime Profile
    │
    ▼
Random Forest Model
    │
    ▼
Risk Classification
    │
    ▼
JSON Response
    │
    ▼
Flutter Safety UI
```

Example response:

```json
{
    "district": "Mangalore",
    "risk_level": "Moderate",
    "risk_score": 0.62
}
```

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_BACKEND_REPOSITORY_URL>
cd SafeYatra-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=SafeYatra

GOOGLE_MAPS_API_KEY=your_google_maps_api_key

FIREBASE_PROJECT_ID=your_firebase_project_id
```

Do **not** commit `.env` or API keys to GitHub.

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

## Flutter Integration

The Flutter application communicates with the FastAPI backend through REST APIs.

```text
Flutter
   │
   │ HTTP Request
   ▼
FastAPI
   │
   ├── MongoDB
   ├── Random Forest
   ├── Google APIs
   └── Firebase
   │
   ▼
JSON Response
   │
   ▼
Flutter
```

This keeps the machine learning and database logic on the backend while allowing the Flutter application to remain lightweight.

## Future Improvements

* Real-time authority integration
* Live crowd-sourced safety signals
* LSTM-based abnormal movement detection
* Improved route recommendation system
* Offline safety prediction
* Multilingual backend services
* Scalable deployment using Docker
* Cloud deployment and load balancing
* Real-time WebSocket-based tourist tracking

## Authors

* Ramaprasad Nayak
* Ryan Savio Sequeira
* Prem Sagar Phulsay
* Pratheek

## Institution

**Department of CSE – Artificial Intelligence and Machine Learning**
**Mangalore Institute of Technology & Engineering (MITE)**
Moodbidri, Mangalore, India

## License

This project is developed for academic and research purposes.
