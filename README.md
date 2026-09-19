# 🚨 AI Emergency Resource Coordinator

An AI-powered emergency response coordination platform that helps analyze emergency incidents, forecast resource demand, and coordinate ambulances, hospitals, rescue teams, weather intelligence, routing, and AI-assisted emergency recommendations.

The project combines **Python, Machine Learning, Generative AI, Optimization, APIs, SQLite, SQLAlchemy, and Streamlit** into a single emergency coordination platform.

---

## 📌 Overview

The **AI Emergency Resource Coordinator** is a decision-support prototype designed to demonstrate how AI and Data Science can assist emergency response coordination.

The system processes emergency incident information and coordinates multiple resources such as:

- 🚑 Ambulances
- 🏥 Hospitals
- 🚒 Rescue Teams
- 🌦️ Weather Information
- 🗺️ Emergency Routes
- 🤖 Generative AI Recommendations
- 📊 Demand Forecasting
- 🔔 Emergency Notifications

The complete workflow is presented through an interactive **Streamlit dashboard**.

---

## ✨ Key Features

- Emergency incident management
- Historical emergency incident analysis
- SQLite database
- SQLAlchemy ORM
- CRUD operations for emergency resources
- Machine Learning based demand forecasting
- Emergency severity prediction
- Ambulance selection
- Hospital recommendation
- Rescue team selection
- Emergency route calculation
- Weather intelligence
- Generative AI emergency recommendations
- Emergency notification generation
- Interactive emergency maps
- Streamlit dashboard
- Modular agent-based architecture
- API integrations
- Gemini API fallback handling

---

## 🏗️ System Architecture

```text
                    ┌───────────────────────┐
                    │   Emergency Incident  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Incident Analysis   │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
       │  Ambulance  │   │   Hospital  │   │ Rescue Team │
       │  Selection  │   │  Selection  │   │  Selection  │
       └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Weather Intelligence  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Route Calculation   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Demand Forecasting   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     Generative AI     │
                    │ Gemini Recommendation │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │Emergency Notification │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Streamlit Dashboard  │
                    └───────────────────────┘
```

---

## 🤖 AI & Machine Learning

The project uses Machine Learning for emergency demand forecasting and severity prediction.

### 📈 Demand Forecasting

The demand forecasting model uses historical emergency incident information.

**Features**

```text
day_of_week
day_of_month
month
week_of_year
lag_1
lag_7
rolling_7
```

**Forecasting Pipeline**

```text
Historical Incident Data
          │
          ▼
Daily Incident Aggregation
          │
          ▼
Feature Engineering
          │
          ▼
Lag Features
          │
          ▼
Rolling Features
          │
          ▼
Random Forest Regression
          │
          ▼
Predicted Emergency Demand
```

### 🚨 Emergency Severity Prediction

The project also contains a Machine Learning pipeline for emergency severity prediction.

**Features**

```text
incident_type
reported_victims
weather_condition
response_time_minutes
latitude
longitude
```

The severity model uses preprocessing and Machine Learning techniques to predict emergency severity.

---

## 🚑 Ambulance Optimization

The ambulance optimizer identifies an available ambulance based on emergency location and resource availability.

The workflow considers:

- Ambulance availability
- Ambulance location
- Distance from incident
- Emergency coordination requirements

**Example:**

```text
Emergency Incident
        │
        ▼
Find Available Ambulances
        │
        ▼
Calculate Distance
        │
        ▼
Select Suitable Ambulance
```

---

## 🏥 Hospital Selection

The system identifies a suitable hospital based on:

- Hospital availability
- Available beds
- Hospital location
- Distance from incident

**Example:**

```text
Emergency Incident
        │
        ▼
Available Hospitals
        │
        ▼
Check Available Beds
        │
        ▼
Calculate Distance
        │
        ▼
Select Suitable Hospital
```

---

## 🚒 Rescue Team Selection

The system identifies an available rescue team based on:

- Team availability
- Team location
- Distance from emergency incident
- Emergency requirements

---

## 🌦️ Weather Intelligence

The application retrieves current weather information using a weather API.

Weather information includes:

- Temperature
- Humidity
- Weather condition
- Wind speed

The weather information becomes part of the emergency coordination context.

**Example:**

```text
Emergency Location
        │
        ▼
Weather API
        │
        ▼
Temperature
Humidity
Weather Condition
Wind Speed
        │
        ▼
Emergency Coordination
```

---

## 🗺️ Emergency Route Calculation

The project integrates Geoapify routing services for emergency route calculation.

The route workflow calculates:

- Route distance
- Estimated travel time

**Example:**

```text
Selected Ambulance
        │
        ▼
Emergency Location
        │
        ▼
Geoapify Routing API
        │
        ▼
Route Distance
        │
        ▼
Estimated Travel Time
```

The calculated route can also be displayed on the emergency map.

---

## 🤖 Generative AI

The project integrates Google Gemini Generative AI using the `google-genai` package.

Gemini receives the coordinated emergency information and generates an emergency response recommendation.

The AI recommendation can include:

- Emergency situation summary
- Predicted demand
- Selected ambulance
- Selected hospital
- Selected rescue team
- Route distance
- Estimated travel time
- Current weather
- Recommended emergency actions

### Gemini Workflow

```text
Emergency Data
      │
      ▼
Resource Selection
      │
      ▼
Weather Information
      │
      ▼
Route Information
      │
      ▼
Demand Forecast
      │
      ▼
Gemini
      │
      ▼
AI Emergency Recommendation
```

### 🛡️ Gemini API Fallback

The application contains fallback handling for temporary Gemini API failures.

If Gemini is temporarily unavailable, the application generates a fallback response instead of stopping the complete emergency coordination workflow.

```text
Gemini API
    │
    ├── Success ───────► AI Recommendation
    │
    └── Failure ───────► Fallback Response
```

This helps keep the application operational during temporary API availability issues.

---

## 📊 Streamlit Dashboard

The application provides an interactive Streamlit dashboard.

The dashboard contains sections such as:

- Current Emergency
- Emergency Statistics
- Emergency Analytics
- Emergency Map
- Selected Ambulance
- Selected Hospital
- Selected Rescue Team
- Emergency Route
- Current Weather
- AI Emergency Recommendation
- Emergency Notification

### ▶️ Run the Dashboard

From the project root directory:

```bash
streamlit run dashboard/dashboard.py
```

The Streamlit application will open in the browser.

---

## 🗄️ Database

The project uses:

- SQLite
- SQLAlchemy

**Database file:**

```text
emergency.db
```

**Tables / Entities:**

- Incidents
- Hospitals
- Ambulances
- Rescue Teams
- Victims

The project also contains repository modules for database operations and CRUD functionality.

---

## 📁 Project Structure

```text
AI-Emergency-Resource-Coordinator/
│
├── app/
│   │
│   ├── agents/
│   │   ├── coordinator_agent.py
│   │   ├── forecast_agent.py
│   │   ├── hospital_agent.py
│   │   ├── incident_agent.py
│   │   ├── optimization_agent.py
│   │   ├── resource_agent.py
│   │   ├── route_agent.py
│   │   └── victim_agent.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   ├── init_database.py
│   │   ├── models.py
│   │   ├── seed_database.py
│   │   ├── seed_historical_incidents.py
│   │   └── repositories/
│   │       ├── hospital_repository.py
│   │       ├── incident_repository.py
│   │       └── resource_repository.py
│   │
│   ├── ml/
│   │   ├── demand_model.py
│   │   ├── severity_model.py
│   │   ├── preprocessing.py
│   │   ├── evaluation.py
│   │   └── models/
│   │
│   ├── optimization/
│   │   ├── ambulance_optimizer.py
│   │   ├── resource_allocator.py
│   │   └── route_optimizer.py
│   │
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── maps_service.py
│   │   ├── notification_service.py
│   │   └── weather_service.py
│   │
│   ├── simulation/
│   ├── utils/
│   ├── workflows/
│   ├── config.py
│   └── main.py
│
├── dashboard/
│   ├── dashboard.py
│   │
│   ├── components/
│   │   ├── cards.py
│   │   ├── charts.py
│   │   └── maps.py
│   │
│   └── pages/
│       ├── analytics.py
│       ├── hospitals.py
│       ├── incidents.py
│       ├── live_map.py
│       └── resources.py
│
├── data/
│   └── raw/
│       ├── ambulances.csv
│       ├── hospitals.csv
│       ├── incidents.csv
│       ├── rescue_teams.csv
│       └── victims.csv
│
├── docs/
│   ├── api_documentation.md
│   ├── architecture.md
│   └── workflow.md
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_severity_model.ipynb
│   └── 03_demand_forecasting.ipynb
│
├── scripts/
│   ├── generate_data.py
│   ├── seed_database.py
│   └── train_models.py
│
├── tests/
│   ├── test_agents.py
│   ├── test_ml.py
│   ├── test_optimization.py
│   └── test_services.py
│
├── emergency.db
├── image.png
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Model Persistence | Joblib |
| Database | SQLite, SQLAlchemy |
| Dashboard | Streamlit |
| Visualization | Plotly, Matplotlib, Seaborn |
| Mapping | Folium, Streamlit-Folium |
| Generative AI | Google Gemini, google-genai |
| Weather API | Weather API |
| Routing API | Geoapify |
| Environment Management | python-dotenv |
| Testing | Python Test Modules |

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Emergency-Resource-Coordinator.git
```

Move into the project directory:

```bash
cd AI-Emergency-Resource-Coordinator
```

### 2. Create Virtual Environment

**Windows**

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_api_key
GEOAPIFY_API_KEY=your_geoapify_api_key
```

> **⚠️ Important**
>
> Never upload your real API keys to GitHub.
>
> The `.env` file is included in `.gitignore`.
>
> Use `.env.example` as the configuration template.

---

## ▶️ Run the Application

Make sure you are inside the project root.

Then run:

```bash
streamlit run dashboard/dashboard.py
```

The application will start and open the Streamlit dashboard.

---

## 🧪 Testing

The project contains test modules for different components.

```text
tests/
├── test_agents.py
├── test_ml.py
├── test_optimization.py
└── test_services.py
```

The project has been tested across major components including:

- Database operations
- Incident repository
- Hospital repository
- Resource repository
- Demand forecasting
- Severity prediction
- Ambulance optimization
- Hospital selection
- Rescue team selection
- Route calculation
- Weather service
- Notification service
- AI recommendation
- End-to-end emergency coordination
- Streamlit dashboard

---

## 📌 Example Emergency Coordination Flow

```text
┌───────────────────────────┐
│     Emergency Incident    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    Incident Processing    │
└─────────────┬─────────────┘
              │
       ┌──────┼──────┐
       │      │      │
       ▼      ▼      ▼
   Ambulance Hospital Rescue
   Selection Selection Team
       │      │      │
       └──────┼──────┘
              │
              ▼
      Weather Intelligence
              │
              ▼
       Route Calculation
              │
              ▼
       Demand Forecasting
              │
              ▼
        Gemini AI Analysis
              │
              ▼
    Emergency Recommendation
              │
              ▼
     Notification Generation
              │
              ▼
       Streamlit Dashboard
```

---

## 📊 Demo Data

The project includes a local SQLite database and raw CSV datasets for development and demonstration.

**Raw datasets include:**

- `ambulances.csv`
- `hospitals.csv`
- `incidents.csv`
- `rescue_teams.csv`
- `victims.csv`

The local demonstration database contains emergency incidents and emergency resources used for testing and dashboard visualization.

Database contents may change during development, testing, simulations, and CRUD operations.

---

## 📚 Documentation

Additional project documentation is available in the `docs/` directory.

```text
docs/
├── api_documentation.md
├── architecture.md
└── workflow.md
```

---

## 🚀 Future Enhancements

Potential future improvements include:

- Real-time GPS tracking
- Real-time emergency alerts
- Multi-incident resource optimization
- Advanced time-series forecasting
- GIS-based emergency risk mapping
- Real-time data streaming
- Mobile application
- Computer vision based incident detection
- Live ambulance tracking
- Advanced route optimization
- Multi-agent emergency coordination
- Historical emergency trend analysis

---

## ⚠️ Disclaimer

This project is an AI-assisted prototype created for educational, portfolio, and demonstration purposes.

It is not intended to replace:

- Trained emergency personnel
- Official emergency response systems
- Medical professionals
- Emergency dispatch authorities
- Real-world emergency decision-making systems

AI-generated recommendations and resource selections should be treated as decision-support outputs and must be validated by qualified personnel before being used in real-world emergency situations.

---

## 👨‍💻 Author

**Ajay Dnyaneshwar Pawar**

Data Science & AI | Python | SQL | Machine Learning | Generative AI

---

## ⭐ Project Highlights

This project demonstrates practical experience with:

```text
Python
│
├── Data Science
│
├── Machine Learning
│
├── Generative AI
│
├── Database Management
│
├── API Integration
│
├── Optimization
│
├── Data Visualization
│
├── Streamlit
│
└── End-to-End AI Application Development
```

---

⭐ If you find this project useful, consider giving the repository a star.
