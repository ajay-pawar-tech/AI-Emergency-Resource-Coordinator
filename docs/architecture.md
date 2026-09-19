# 🏗️ System Architecture

The **AI Emergency Resource Coordinator** follows a modular architecture that combines a Streamlit user interface, SQLite database, AI agents, machine-learning models, optimization algorithms, routing services, weather intelligence, and Generative AI.

---

## 1. High-Level Architecture

```text
                    ┌──────────────────────────┐
                    │     Streamlit Dashboard  │
                    │                          │
                    │  Dashboard               │
                    │  Live Map                │
                    │  Incidents               │
                    │  Hospitals               │
                    │  Resources               │
                    │  Analytics               │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     Coordinator Agent    │
                    │                          │
                    │ Coordinates the complete  │
                    │ emergency workflow       │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
      ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
      │ Incident     │   │ Victim       │   │ Resource     │
      │ Agent        │   │ Agent        │   │ Agent        │
      └──────┬───────┘   └──────────────┘   └──────┬───────┘
             │                                      │
             │                                      ▼
             │                            ┌─────────────────┐
             │                            │ Hospital Agent  │
             │                            └─────────────────┘
             │
             ▼
      ┌──────────────────┐
      │ Forecast Agent   │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Optimization     │
      │ Agent            │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Route Agent      │
      └────────┬─────────┘
               │
        ┌──────┴───────────┐
        ▼                  ▼
┌───────────────┐  ┌────────────────┐
│ Weather       │  │ Generative AI  │
│ Service       │  │ Service        │
└───────────────┘  └────────────────┘
               │
               ▼
      ┌──────────────────┐
      │ SQLite Database  │
      │ emergency.db    │
      └──────────────────┘