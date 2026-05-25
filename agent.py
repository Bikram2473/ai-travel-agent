from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from state import TripState
from tools import fetch_flight_price, fetch_hotel_tiers, fetch_weather

class PlannerDecision(BaseModel):
    origin_airport: str = Field(description="3-letter IATA code of origin airport, e.g., BOM")
    destination_airport: str = Field(description="3-letter IATA code of destination airport, e.g., BBI")
    travel_date: str = Field(description="Departure date in strict YYYY-MM-DD format. Must be a future date.")
    duration_nights: int = Field(description="Number of nights for hotel accommodation.")
    hotel_tier: str = Field(description="MUST choose exactly one: 'budget', 'standard', or 'luxury'.")
    proposed_itinerary: str = Field(description="A descriptive itinerary outline for the stay.")

def planner_node(state: TripState) -> dict:
    print(f"\n--- [Node] Running Planner (Iteration {state['iterations'] + 1}) ---")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    structured_llm = llm.with_structured_output(PlannerDecision)
    
    current_weather = fetch_weather(state['destination'])
    print(f"   [Context] Destination Weather: {current_weather}")
    
    # --- NEW: Added explicit formatting instructions here! ---
    base_prompt = (
        f"You are an expert autonomous travel planner.\n"
        f"The user wants to travel from {state['origin']} to {state['destination']}.\n"
        f"Target Budget: ₹{state['budget']} INR\n"
        f"Destination Weather Forecast: {current_weather}\n\n"
        f"CRITICAL INSTRUCTION 1 (Weather): You must tailor the 'proposed_itinerary' to the weather. "
        f"If it is raining or extremely hot, prioritize indoor activities. "
        f"If it is clear, prioritize outdoor sightseeing.\n\n"
        f"CRITICAL INSTRUCTION 2 (Formatting): You MUST format the 'proposed_itinerary' using clean Markdown. "
        f"Use bold headers for each day (e.g., **Day 1: Arrival**) and bullet points for the activities so it is highly readable. "
        f"Do NOT output a giant block of text.\n\n"
    )
    # ---------------------------------------------------------
    
    if state["status"] == "budget_exceeded":
        correction_prompt = (
            f"⚠️ CRITICAL REMINDER: Your previous attempt failed. It cost a total of ₹{state['total_cost']} "
            f"(Flights: ₹{state['flight_cost']}, {state['hotel_tier'].title()} Hotel: ₹{state['hotel_cost']}), "
            f"which exceeded the maximum ₹{state['budget']}.\n"
            f"To fix this, you should either:\n"
            f"1. Downgrade the 'hotel_tier'.\n"
            f"2. Reduce the 'duration_nights' to fit within the budget.\n"
            f"History logs:\n{state['log_history']}\n"
        )
        full_prompt = base_prompt + correction_prompt
    else:
        full_prompt = base_prompt + f"Target execution date window context is {state['dates']}."

    response = structured_llm.invoke(full_prompt)
    
    return {
        "origin": response.origin_airport,
        "destination": response.destination_airport,
        "dates": response.travel_date,
        "duration_days": response.duration_nights,
        "hotel_tier": response.hotel_tier.lower(),
        "current_itinerary": response.proposed_itinerary,
        "weather_forecast": current_weather, 
        "status": "searching"
    }

def researcher_node(state: TripState) -> dict:
    print(f"--- [Node] Running Researcher (Querying SerpApi) ---")
    
    flight_data = fetch_flight_price(state["origin"], state["destination"], state["dates"])
    f_cost = flight_data["price"]
    f_link = flight_data["link"]
    
    hotel_tiers = fetch_hotel_tiers(state["destination"], state["dates"], state["duration_days"])
    
    chosen_tier = state.get("hotel_tier", "standard")
    if chosen_tier not in ["budget", "standard", "luxury"]:
        chosen_tier = "standard"
        
    h_cost = float(hotel_tiers[chosen_tier])
    t_cost = f_cost + h_cost
    
    print(f"   Flight cost found: ₹{f_cost:,.2f}")
    print(f"   Hotel cost found ({chosen_tier} tier): ₹{h_cost:,.2f}")
    print(f"   Calculated total: ₹{t_cost:,.2f}")
    
    return {
        "flight_cost": f_cost,
        "flight_booking_link": f_link, 
        "hotel_cost": h_cost,
        "total_cost": t_cost
    }

def auditor_node(state: TripState) -> dict:
    print(f"--- [Node] Running Auditor (Checking Budget Requirements) ---")
    
    new_log = f"- Attempt {state['iterations']+1}: {state['duration_days']} nights at {state['hotel_tier']} tier costed ₹{state['total_cost']}\n"
    current_history = state.get("log_history", "") + new_log
    
    if state["total_cost"] <= state["budget"]:
        print("✅ Success! Plan matches within budget bounds.")
        return {"status": "success", "log_history": current_history}
    else:
        new_iterations = state["iterations"] + 1
        if new_iterations >= 5:
            print("❌ Failure: Maximum routing correction depth hit.")
            return {"status": "failed", "log_history": current_history, "iterations": new_iterations}
        else:
            print(f"⚠️ Budget Exceeded (₹{state['total_cost']} > ₹{state['budget']}). Triggering graph loop...")
            return {"status": "budget_exceeded", "log_history": current_history, "iterations": new_iterations}

def routing_logic(state: TripState):
    if state["status"] in ["success", "failed"]:
        return END
    return "planner"

workflow = StateGraph(TripState)
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("auditor", auditor_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "auditor")
workflow.add_conditional_edges("auditor", routing_logic)

compiled_agent = workflow.compile()