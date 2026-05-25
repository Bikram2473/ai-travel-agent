import os
import requests
from datetime import datetime, timedelta
import tempfile
from fpdf import FPDF
from geopy.geocoders import Nominatim
import folium
from dotenv import load_dotenv

load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def fetch_flight_price(origin: str, destination: str, date: str) -> dict:
    """Queries SerpApi (Google Flights) to find the cheapest flight and link."""
    fallback_link = f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{date}"
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_flights",
            "departure_id": origin.upper().strip(),
            "arrival_id": destination.upper().strip(),
            "outbound_date": date,
            "currency": "INR",
            "hl": "en",
            "api_key": SERPAPI_API_KEY
        }
        res = requests.get(url, params=params)
        data = res.json()

        if "best_flights" in data and len(data["best_flights"]) > 0:
            flight = data["best_flights"][0]
            price = float(flight["price"])
            link = flight.get("shareable_url", fallback_link)
            return {"price": price, "link": link}
    except Exception as e:
        print(f"    [Tool Alert] Flight lookup failed: {e}. Utilizing fallback.")

    return {"price": 8500.0, "link": fallback_link}

def fetch_hotel_tiers(destination: str, check_in_date: str, duration_days: int) -> dict:
    """Queries SerpApi (Google Hotels) and calculates stay costs."""
    try:
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = check_in + timedelta(days=duration_days)
        
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_hotels",
            "q": destination,
            "check_in_date": check_in.strftime("%Y-%m-%d"),
            "check_out_date": check_out.strftime("%Y-%m-%d"),
            "currency": "INR",
            "hl": "en",
            "api_key": SERPAPI_API_KEY
        }
        res = requests.get(url, params=params)
        data = res.json()

        if "properties" in data and len(data["properties"]) > 0:
            prices = []
            for prop in data["properties"]:
                if "rate_per_night" in prop and "extracted_lowest" in prop["rate_per_night"]:
                    prices.append(prop["rate_per_night"]["extracted_lowest"])
            
            if len(prices) >= 3:
                prices.sort()
                return {
                    "budget": prices[0] * duration_days,
                    "standard": prices[len(prices)//2] * duration_days,
                    "luxury": prices[-1] * duration_days
                }
    except Exception as e:
        print(f"    [Tool Alert] Hotel lookup failed: {e}. Utilizing dynamic fallback.")

    return {
        "budget": 1500.0 * duration_days,
        "standard": 3500.0 * duration_days,
        "luxury": 8500.0 * duration_days
    }

def fetch_weather(destination_code: str) -> str:
    """Fetches real-time weather conditions."""
    try:
        res = requests.get(f"https://wttr.in/{destination_code}?format=%C+%t")
        if res.status_code == 200:
            return res.text.strip()
    except Exception as e:
        print(f"    [Tool Alert] Weather lookup failed: {e}")
    return "Clear +25°C"

def generate_ics(destination: str, start_date: str, duration: int, itinerary: str) -> str:
    """Generates a standard iCalendar format string."""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=duration)
        
        dtstart = start_dt.strftime("%Y%m%d")
        dtend = end_dt.strftime("%Y%m%d")
        clean_desc = itinerary.replace('\n', '\\n')
        
        return (
            "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\n"
            f"DTSTART;VALUE=DATE:{dtstart}\nDTEND;VALUE=DATE:{dtend}\n"
            f"SUMMARY:Trip to {destination}\nDESCRIPTION:{clean_desc}\n"
            "END:VEVENT\nEND:VCALENDAR"
        )
    except Exception:
        return ""

def generate_pdf_brochure(destination: str, dates: str, duration: int, tier: str, total_cost: float, itinerary: str) -> bytes:
    """Generates a beautifully styled PDF Travel Brochure."""
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 114, 255)
    pdf.cell(0, 15, txt=f"Your AI-Optimized Trip to {destination}", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(30, 41, 59)
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    pdf.cell(0, 10, txt=f"Departure: {dates}   |   Duration: {duration} Nights", ln=True)
    pdf.cell(0, 10, txt=f"Hotel Tier: {tier.title()}   |   Total Budget Used: INR {total_cost:,.2f}", ln=True)
    pdf.line(10, 55, 200, 55)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Daily Itinerary:", ln=True)
    pdf.set_font("Arial", '', 11)
    
    clean_itinerary = itinerary.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean_itinerary)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            pdf_bytes = f.read()
            
    return pdf_bytes

def generate_map(destination_code: str):
    """Geocodes the destination and returns an interactive Folium Map."""
    try:
        geolocator = Nominatim(user_agent="ai_travel_agent")
        location = geolocator.geocode(f"{destination_code} Airport") 
        
        if location:
            lat, lon = location.latitude, location.longitude
        else:
            lat, lon = 20.5937, 78.9629 # India fallback
            
        m = folium.Map(location=[lat, lon], zoom_start=11, tiles="CartoDB positron")
        folium.Marker(
            [lat, lon], 
            popup=f"Arrival: {destination_code}", 
            tooltip="Your Destination",
            icon=folium.Icon(color="blue", icon="plane")
        ).add_to(m)
        
        folium.Circle(
            radius=15000, location=[lat, lon], color="#0072ff", fill=True, fill_opacity=0.1
        ).add_to(m)
        
        return m
    except Exception:
        return None