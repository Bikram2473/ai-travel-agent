# ✈️ AI Agentic Travel Planner

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-green.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)

An enterprise-grade, autonomous AI travel planning agent built to negotiate and optimize travel itineraries dynamically. 

Unlike standard conversational chatbots that simply generate text, this system utilizes a **stateful, multi-node agentic workflow**. It accounts for real-world constraints such as live flight pricing, budget limits, hotel tiers, and real-time weather forecasts to deliver a fully personalized, actionable, and budget-approved trip.

---

## ✨ Key Features (The "Wow" Factor)

* **🧠 Multi-Agent Orchestration:** Uses LangGraph to recursively route tasks between an AI Planner, a Data Researcher, and a Budget Auditor until the user's constraints are met.
* **🌦️ Context-Aware Reasoning:** Ingests live weather data (via `wttr.in`) to dynamically alter itinerary suggestions (e.g., suggesting indoor museums during heavy rain or extreme heat).
* **🗺️ Interactive Mapping:** Automatically geocodes destinations and renders an interactive, pannable world map directly in the UI using `Folium`.
* **⚡ One-Click Execution:** Bridges the gap between planning and execution with three export actions:
  * **Book Flights:** Generates a live, click-to-book Google Flights URL for the cheapest found fare.
  * **Add to Calendar:** Instantly compiles the itinerary into a downloadable `.ics` file for Apple/Google Calendar.
  * **Download PDF:** Formats the budget report and daily itinerary into a beautiful, downloadable PDF brochure.

---

## 🚀 Complete Installation & Setup Guide

Follow these sequential terminal commands to stand up the project within a clean local environment:

### 1. Repository Preparation
```bash
git clone [https://github.com/Bikram2473/ai-travel-agent.git](https://github.com/Bikram2473/ai-travel-agent.git)
cd ai-travel-agent
```

### 2. Create a Virtual Environment 
```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Code Snippet
```bash
# Get this from Google AI Studio
GOOGLE_API_KEY=your_gemini_api_key_here

# Get this from SerpApi.com
SERPAPI_API_KEY=your_serpapi_key_here
```

### 5. Launch the Application
```bash
streamlit run app.py
```

Open your web browser to http://localhost:8501 to start planning!
