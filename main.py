from dotenv import load_dotenv
from agent import compiled_agent

load_dotenv()

def run_trip_planner():
    print("=============================================")
    print("  Welcome to Autonomous Agentic Trip Planner  ")
    print("=============================================\n")
    
    initial_input = {
        "origin": "BOM",
        "destination": "BBI",
        "dates": "2026-07-12",
        "duration_days": 4,
        "budget": float(budget),
        "hotel_tier": "luxury",                               # We start by demanding luxury
        "current_itinerary": "Pending generation...",
        "flight_cost": 0.0,
        "hotel_cost": 0.0,
        "total_cost": 0.0,
        "iterations": 0,
        "status": "planning",
        "log_history": ""
    }
    
    final_state = compiled_agent.invoke(initial_input)
    
    print("\n=============================================")
    print("               FINAL RESULTS                 ")
    print("=============================================")
    print(f"Final Status: {final_state.get('status', 'UNKNOWN').upper()}")
    print(f"Total Iterations: {final_state.get('iterations', 0)}")
    print(f"Optimized Destination Chosen: {final_state.get('destination', 'N/A')}")
    print(f"Confirmed Departure Date: {final_state.get('dates', 'N/A')}")
    
    tier = final_state.get('hotel_tier', 'unknown').upper()
    nights = final_state.get('duration_days', 0)
    print(f"Optimized Stay: {nights} Nights in a {tier} hotel")
    
    total = final_state.get('total_cost', 0)
    budget = final_state.get('budget', 15000)
    print(f"Final Verified Total Price: ₹{total:,.2f} (Target Budget Limit: ₹{budget:,.2f})")
    
    itinerary = final_state.get('current_itinerary', 'No itinerary generated.')
    print(f"\nFinal Itinerary Plan Summary:\n{itinerary}")
    print("=============================================")

if __name__ == "__main__":
    run_trip_planner()