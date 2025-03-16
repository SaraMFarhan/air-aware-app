import streamlit as st
import plotly.graph_objects as go
import random
import math
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Air Aware",
    page_icon="🌱",
    layout="wide"
)

# Dictionary of Saudi Arabian cities with their coordinates
SAUDI_CITIES = {
    "Riyadh": {"lat": 24.7136, "lon": 46.6753},
    "Jeddah": {"lat": 21.5433, "lon": 39.1728},
    "Mecca": {"lat": 21.3891, "lon": 39.8579},
    "Medina": {"lat": 24.5247, "lon": 39.5692},
    "Dammam": {"lat": 26.4207, "lon": 50.0888},
    "Tabuk": {"lat": 28.3998, "lon": 36.5715},
    "Abha": {"lat": 18.2164, "lon": 42.5053},
    "Al Khobar": {"lat": 26.2794, "lon": 50.2083},
    "Khamis Mushait": {"lat": 18.3000, "lon": 42.7333},
    "Taif": {"lat": 21.2871, "lon": 40.4158}
}

# Dictionary of city images with width parameter already added
CITY_IMAGES = {
    "Riyadh": "https://images.unsplash.com/photo-1586724237569-f3d0c1dee8c6?w=800",
    "Jeddah": "https://images.unsplash.com/photo-1622147077407-afe05d9a6ffc?w=800",
    "Mecca": "https://images.unsplash.com/photo-1580418827493-f2b22c0a76cb?w=800",
    "Medina": "https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa?w=800",
    "Dammam": "https://images.unsplash.com/photo-1578895101408-1a6b23e12d16?w=800",
    "Tabuk": "https://images.unsplash.com/photo-1516339626902-7dee9238d83a?w=800",
    "Abha": "https://images.unsplash.com/photo-1543853258-304b02c31a8a?w=800",
    "Al Khobar": "https://images.unsplash.com/photo-1568866381492-ea4a6db0f501?w=800",
    "Khamis Mushait": "https://images.unsplash.com/photo-1561531061-0cb23b0c8ab3?w=800",
    "Taif": "https://images.unsplash.com/photo-1547558918-7ae92c6466ef?w=800",
    "default": "https://images.unsplash.com/photo-1517429128955-67059d52def3?w=800"
}

# Eco-friendly transport images with width parameter
ECO_TRANSPORT_IMAGES = [
    "https://images.unsplash.com/photo-1519664824562-b4bc73f9795a?w=800",  # Walking
    "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800",  # Cycling
    "https://images.unsplash.com/photo-1556122071-a221fac50430?w=800",  # Public Transport
    "https://images.unsplash.com/photo-1617886322168-72b886574cf7?w=800",  # EV
    "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?w=800",  # Modern tram
    "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800",  # Bicycles
    "https://images.unsplash.com/photo-1529946179074-87642f6204d7?w=800"   # Electric bus
]

# CSS styles
css = """
.stApp {
    max-width: 1200px;
    margin: 0 auto;
}

.main-header {
    color: #00875A;
    text-align: center;
    margin-bottom: 2rem;
}

.gold-text {
    color: #DAA520;
}

.city-select {
    background-color: #F0F2F6;
    padding: 1rem;
    border-radius: 10px;
}

.metrics-container {
    background-color: #F8F9FA;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #E9ECEF;
}

.reward-card {
    background-color: #FAFDF7;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #00875A;
    margin: 1rem 0;
}

.suggestion-card {
    background-color: #FFF8DC;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #DAA520;
    margin: 1rem 0;
}

div.stButton > button {
    background-color: #00875A;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
}

div.stButton > button:hover {
    background-color: #006B48;
}
"""

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Utility Functions
def find_nearest_city(lat, lon):
    """Find the nearest city to a given latitude and longitude"""
    nearest_city = None
    min_distance = float('inf')

    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers using Haversine formula"""
        # Earth radius in kilometers
        R = 6371.0

        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Difference in coordinates
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance

    for city, coords in SAUDI_CITIES.items():
        distance = calculate_distance(lat, lon, coords["lat"], coords["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest_city = city

    return nearest_city, min_distance

def is_in_saudi_arabia(lat, lon):
    """Check if coordinates are within Saudi Arabia's approximate boundaries"""
    # Approximate bounding box for Saudi Arabia
    min_lat, max_lat = 16.3, 32.1
    min_lon, max_lon = 34.5, 55.7

    return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)

def get_aqi_description(aqi):
    """
    Get description and color code for AQI value
    """
    if aqi < 2:
        return "Good", "#00C853"  # Green
    elif aqi < 3:
        return "Moderate", "#FFD600"  # Yellow
    elif aqi < 4:
        return "Unhealthy for Sensitive Groups", "#FF9100"  # Orange
    else:
        return "Unhealthy", "#FF3D00"  # Red

def get_air_quality(lat, lon):
    """
    Get air quality data for the given coordinates using OpenWeather API
    """
    api_key = "769ef70d6cdc1edfd61ae12ccf9e929b"  # Replace with your OpenWeather API key
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        aqi = data["list"][0]["main"]["aqi"]
        components = data["list"][0]["components"]
        
        return {
            "aqi": aqi,
            "components": components
        }
    except requests.RequestException as e:
        st.error(f"Error fetching air quality data: {str(e)}")
        return None

# Rewards System
class RewardsSystem:
    def __init__(self):
        if "user_points" not in st.session_state:
            st.session_state.user_points = 0
        if "eco_actions" not in st.session_state:
            st.session_state.eco_actions = []

    def add_eco_action(self, action_type, points):
        """
        Record an eco-friendly action and award points
        """
        st.session_state.user_points += points
        st.session_state.eco_actions.append({
            "action": action_type,
            "points": points,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    def get_points(self):
        return st.session_state.user_points

    def get_recent_actions(self, limit=5):
        return list(reversed(st.session_state.eco_actions))[:limit]

    @staticmethod
    def get_rewards_tiers():
        return {
            "Green Seedling": 100,
            "Eco Warrior": 500,
            "Climate Champion": 1000,
            "Environmental Hero": 2000
        }

    def get_current_tier(self):
        points = self.get_points()
        tiers = self.get_rewards_tiers()
        current_tier = "Newcomer"
        
        for tier, threshold in tiers.items():
            if points >= threshold:
                current_tier = tier
        
        return current_tier

# App Functionality
def create_aqi_gauge(aqi):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [1, 5], 'tickwidth': 1},
            'bar': {'color': get_aqi_description(aqi)[1]},
            'steps': [
                {'range': [1, 2], 'color': "#00C853"},
                {'range': [2, 3], 'color': "#FFD600"},
                {'range': [3, 4], 'color': "#FF9100"},
                {'range': [4, 5], 'color': "#FF3D00"}
            ]
        }
    ))
    fig.update_layout(height=250)
    return fig

def get_transport_suggestions(aqi):
    suggestions = []
    if aqi >= 3:
        suggestions = [
            "🚶‍♂️ Walk for short distances (Earn 50 points)",
            "🚲 Use a bicycle (Earn 75 points)",
            "🚌 Take public transport (Earn 100 points)",
            "🚗 Consider carpooling (Earn 60 points)"
        ]
    return suggestions

def display_transport_image():
    """Display a random transport image with error handling"""
    try:
        image_url = random.choice(ECO_TRANSPORT_IMAGES)
        st.image(image_url, caption="Eco-friendly Transportation Options", use_container_width=True)
    except Exception as e:
        st.warning(f"Unable to load transport image: {str(e)}")

# Initialize rewards system
rewards = RewardsSystem()

# Main App
st.markdown("<h1 class='main-header'>🌱 Air Aware</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #666;'>Saudi Air Quality Monitor</h2>", unsafe_allow_html=True)

# City selection
col1, col2 = st.columns([2, 1])

with col1:
    selected_city = st.selectbox(
        "Select a city",
        options=list(SAUDI_CITIES.keys()),
        key="city_select"
    )

with col2:
    if st.button("📍 Locate Me"):
        try:
            # Get user's location using browser's geolocation
            loc = st.query_params.get('geolocation', None)

            if loc and len(loc) >= 2:
                lat, lon = float(loc[0]), float(loc[1])

                if is_in_saudi_arabia(lat, lon):
                    nearest_city, distance = find_nearest_city(lat, lon)
                    if distance < 100:  # Within 100km
                        selected_city = nearest_city
                        st.success(f"Located you near {selected_city}")
                    else:
                        st.warning("No major Saudi city found near your location")
                else:
                    st.warning("Location outside Saudi Arabia. Please select a city manually.")
            else:
                # Add JavaScript for geolocation with better error handling
                st.markdown("""
                    <script>
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            function(position) {
                                const lat = position.coords.latitude;
                                const lon = position.coords.longitude;
                                const queryParams = new URLSearchParams(window.location.search);
                                queryParams.set('geolocation', `${lat},${lon}`);
                                window.location.search = queryParams.toString();
                            },
                            function(error) {
                                console.error("Geolocation error:", error);
                            },
                            {timeout: 10000}
                        );
                    }
                    </script>
                    """, unsafe_allow_html=True)
                st.info("Please allow location access when prompted")

        except Exception as e:
            st.error("Location service temporarily unavailable")

# Display city image with error handling
try:
    city_image = CITY_IMAGES.get(selected_city, CITY_IMAGES["default"])
    st.image(city_image, caption=f"View of {selected_city}", use_container_width=True)
except Exception as e:
    st.warning(f"Unable to load city image: {str(e)}")

# Fetch and display air quality data
try:
    city_coords = SAUDI_CITIES[selected_city]
    air_data = get_air_quality(city_coords["lat"], city_coords["lon"])

    if air_data:
        aqi = air_data["aqi"]
        description, color = get_aqi_description(aqi)

        # Display AQI information
        st.markdown(f"<h2 class='gold-text'>Air Quality in {selected_city}</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_aqi_gauge(aqi), use_container_width=True)

        with col2:
            st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color: {color}'>Status: {description}</h3>", unsafe_allow_html=True)
            st.markdown("### Pollutant Levels")
            components = air_data["components"]
            for pollutant, value in components.items():
                st.write(f"{pollutant.upper()}: {value:.2f} μg/m³")
            st.markdown("</div>", unsafe_allow_html=True)

        # Transport suggestions
        suggestions = get_transport_suggestions(aqi)
        if suggestions:
            st.markdown("### 🌿 Eco-friendly Transport Suggestions")
            display_transport_image()

            for suggestion in suggestions:
                st.markdown(f"<div class='suggestion-card'>{suggestion}</div>", unsafe_allow_html=True)

        # Rewards section
        st.markdown("### 🏆 Your Eco Rewards")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='reward-card'>", unsafe_allow_html=True)
            st.markdown(f"#### Current Tier: {rewards.get_current_tier()}")
            st.markdown(f"#### Total Points: {rewards.get_points()}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            if st.button("Log Walking Trip"):
                rewards.add_eco_action("Walking", 50)
                st.success("Added 50 points for walking!")

            if st.button("Log Public Transport"):
                rewards.add_eco_action("Public Transport", 100)
                st.success("Added 100 points for using public transport!")

        # Recent activities
        st.markdown("#### Recent Activities")
        for action in rewards.get_recent_actions():
            st.markdown(
                f"<div class='reward-card'>{action['action']}: +{action['points']} points ({action['timestamp']})</div>",
                unsafe_allow_html=True
            )

except Exception as e:
    st.error(f"Error fetching air quality data: {str(e)}")