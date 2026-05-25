import streamlit as st
from dotenv import load_dotenv
from agent import compiled_agent
from tools import generate_ics, generate_pdf_brochure, generate_map
from streamlit_folium import st_folium

load_dotenv()

st.set_page_config(page_title="AI Travel Agent", page_icon="✈️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f4f7f6 !important; }
    h1, h2, h3, h4, h5, h6, p, label, span { color: #1e293b !important; }
    div[data-testid="stForm"] { 
        background-color: white !important; 
        border-radius: 16px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
        padding: 30px; 
        border: none; 
    }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #1e293b !important; 
        border-radius: 8px !important;
        border: none !important;
    }
    input, div[data-baseweb="select"] * {
        color: #ffffff !important; 
        -webkit-text-fill-color: #ffffff !important;
    }
    div[data-testid="stFormSubmitButton"] > button {
        width: 100%; 
        background: linear-gradient(135deg, #0072ff 0%, #00c6ff 100%);
        color: white !important; 
        font-weight: 800; 
        font-size: 1.1rem;
        border-radius: 10px; 
        border: none; 
        padding: 12px; 
        transition: all 0.3s ease;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 8px 20px rgba(0, 114, 255, 0.4); 
        color: white !important;
    }
    div[data-testid="stMetricValue"] > div { 
        color: #0072ff !important; 
        font-weight: 900; 
        font-size: 1.4rem !important; 
        white-space: normal !important; 
        word-wrap: break-word !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("✈️ Smart Agent Travel Planner")

spacer1, main_col, spacer2 = st.columns([1, 3, 1])

with main_col:
    with st.form("trip_form"):
        st.subheader("Plan Your Next Escape")
        st.write("Let the AI negotiate the best itinerary for your budget and the weather.")
        
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input("🛫 From (Origin)", value="BOM", max_chars=3)
            dates = st.date_input("📅 Departure Date").strftime("%Y-%m-%d")
            budget = st.number_input("💰 Max Budget (₹)", min_value=5000, value=15000, step=1000)
        
        with col2:
            destination = st.text_input("🛬 To (Destination)", value="BBI", max_chars=3)
            duration = st.slider("🌙 Duration (Nights)", min_value=1, max_value=14, value=4)
            tier = st.selectbox("🏨 Preferred Hotel Tier", ["budget", "standard", "luxury"], index=2)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("Optimize My Trip")

if submit_button:
    initial_input = {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "dates": dates,
        "duration_days": duration,
        "budget": float(budget),
        "hotel_tier": tier,
        "current_itinerary": "Pending...",
        "flight_cost": 0.0,
        "flight_booking_link": None,
        "hotel_cost": 0.0,
        "total_cost": 0.0,
        "weather_forecast": None, 
        "iterations": 0,
        "status": "planning",
        "log_history": ""
    }
    
    with st.status("🤖 Agent is analyzing APIs, checking weather, and calculating constraints...", expanded=True) as status:
        final_state = compiled_agent.invoke(initial_input)
        status.update(label="Planning Complete!", state="complete", expanded=False)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    res_col1, res_col2, res_col3 = st.columns([1, 2, 1])
    
    with res_col2:
        if final_state.get('status') == "failed":
            st.error(f"❌ Could not optimize a trip within ₹{budget:,.2f} after {final_state.get('iterations')} attempts.")
        else:
            st.success(f"✅ Trip finalized! The agent took {final_state.get('iterations')} iterations to balance your budget.")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(label="Total Cost", value=f"₹{final_state.get('total_cost', 0):,.2f}")
            m2.metric(label="Duration", value=f"{final_state.get('duration_days')} Nights")
            m3.metric(label="Hotel Class", value=final_state.get('hotel_tier', '').title())
            m4.metric(label="Live Weather", value=final_state.get('weather_forecast', 'Unknown'))
            
            st.markdown("### 🗺️ Destination Map")
            with st.spinner("Loading interactive map..."):
                trip_map = generate_map(final_state.get('destination', 'BBI'))
                if trip_map:
                    st_folium(trip_map, width=700, height=350, returned_objects=[])
            
            st.markdown("### 📝 Your Itinerary")
            st.info(final_state.get('current_itinerary', 'No itinerary generated.'))
            
            st.markdown("### 🎯 Actions")
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                st.link_button("✈️ Book Flights", final_state.get("flight_booking_link", "https://google.com/flights"), use_container_width=True)
                
            with action_col2:
                ics_data = generate_ics(final_state.get("destination"), final_state.get("dates"), final_state.get("duration_days"), final_state.get("current_itinerary"))
                st.download_button(label="📅 Add to Calendar", data=ics_data, file_name="trip_itinerary.ics", mime="text/calendar", use_container_width=True)
                
            with action_col3:
                pdf_data = generate_pdf_brochure(
                    final_state.get("destination"), final_state.get("dates"), final_state.get("duration_days"), 
                    final_state.get("hotel_tier"), final_state.get("total_cost"), final_state.get("current_itinerary")
                )
                st.download_button(label="📄 Download PDF", data=pdf_data, file_name="My_Travel_Brochure.pdf", mime="application/pdf", use_container_width=True)
            
            with st.expander("🔍 View AI Reasoning Logs"):
                st.code(final_state.get('log_history', 'No logs available.'), language="text")