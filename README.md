# 🚨 AI Emergency Resource Coordinator

An AI-powered emergency response coordination platform that uses Machine Learning and Generative AI to analyze incidents, forecast emergency demand, and coordinate ambulances, hospitals, and rescue teams.

## 🚀 Key Features

- Emergency Incident Management
- ML-Based Demand Forecasting
- Emergency Severity Prediction
- Intelligent Ambulance & Hospital Selection
- Rescue Team Allocation
- Emergency Route Calculation
- Weather Intelligence
- Gemini AI-Powered Recommendations
- Emergency Notifications
- Interactive Streamlit Dashboard
- SQLite Database & CRUD Operations

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Data Science | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Generative AI | Google Gemini, Groq |
| Database | SQLite, SQLAlchemy |
| Dashboard | Streamlit |
| APIs | Weather API, Geoapify |
| Visualization | Plotly, Matplotlib, Seaborn |

## 🤖 Machine Learning & Generative AI

- Random Forest Regression for emergency demand forecasting.
- Machine Learning pipeline for emergency severity prediction.
- Google Gemini API for AI-generated emergency recommendations.
- Fallback handling for temporary AI API failures.

## ⚙️ Installation & Setup

**1. Clone the Repository**

```bash
git clone https://github.com/ajay-pawar-tech/AI-Emergency-Resource-Coordinator.git
cd AI-Emergency-Resource-Coordinator
```

**2. Create Virtual Environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**

Create a `.env` file and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_weather_api_key
GEOAPIFY_API_KEY=your_geoapify_api_key
```

**5. Run the Application**

```bash
streamlit run dashboard/dashboard.py
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest -v
```

## ⚠️ Disclaimer

This project is an AI-assisted prototype developed for educational and demonstration purposes. It is not a replacement for official emergency response systems or trained emergency personnel.

## 👨‍💻 Author

**Ajay Dnyaneshwar Pawar**

Data Science | Machine Learning | Generative AI

- GitHub: [ajay-pawar-tech](https://github.com/ajay-pawar-tech)
- LinkedIn: [Ajay Pawar](https://www.linkedin.com/in/ajay-pawar-5b101737a/)
