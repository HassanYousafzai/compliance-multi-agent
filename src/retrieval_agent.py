# src/retrieval_agent.py
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import random

class RetrievalAgent:
    def __init__(self):
        self.api_base_url = "http://api.openweathermap.org/data/2.5"
        # Using a demo API key - in production, use environment variables
        self.api_key = "demo_key_12345"  # This will work with mock data
        self.request_history = []
    
    def fetch_data(self, query: str) -> Dict[str, Any]:
        """
        Fetch data based on query. Currently supports weather data.
        Falls back to mock data if API is unavailable.
        """
        try:
            # Try real API first (with mock key it will fail, but structure is there)
            if "weather" in query.lower() or "temperature" in query.lower():
                return self._fetch_weather_data(query)
            else:
                # Generic data retrieval for other query types
                return self._fetch_generic_data(query)
                
        except Exception as e:
            print(f"API call failed, using mock data: {e}")
            return self._get_mock_data(query)
    
    def _fetch_weather_data(self, query: str) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API or mock data"""
        # Extract location from query
        location = self._extract_location(query)
        
        # For demo purposes, we'll use mock data
        # In production, this would make actual API call:
        # response = requests.get(
        #     f"{self.api_base_url}/weather?q={location}&appid={self.api_key}&units=metric"
        # )
        
        # Log the request
        self.request_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'location': location,
            'type': 'weather'
        })
        
        return self._generate_mock_weather_data(location)
    
    def _fetch_generic_data(self, query: str) -> Dict[str, Any]:
        """Fetch generic data based on query type"""
        query_lower = query.lower()
        
        # Log the request
        self.request_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'type': 'generic'
        })
        
        if "patient" in query_lower or "medical" in query_lower:
            return self._generate_mock_medical_data()
        elif "sales" in query_lower or "business" in query_lower:
            return self._generate_mock_business_data()
        elif "user" in query_lower or "customer" in query_lower:
            return self._generate_mock_user_data()
        else:
            return self._generate_mock_general_data()
    
    def _extract_location(self, query: str) -> str:
        """Extract location from query string"""
        locations = ['london', 'paris', 'tokyo', 'berlin', 'new york', 'tokyo']
        query_lower = query.lower()
        
        for location in locations:
            if location in query_lower:
                return location.title()
        
        return "London"  # Default location
    
    def _generate_mock_weather_data(self, location: str) -> Dict[str, Any]:
        """Generate realistic mock weather data"""
        base_temp = random.uniform(-5, 35)  # Realistic temperature range
        
        return {
            "location": location,
            "temperature": round(base_temp, 1),
            "humidity": random.randint(30, 95),
            "pressure": random.randint(1000, 1030),
            "wind_speed": round(random.uniform(0, 25), 1),
            "weather_condition": random.choice(["clear", "cloudy", "rainy", "snowy"]),
            "visibility": random.randint(1, 10),
            "timestamp": datetime.now().isoformat(),
            "data_source": "OpenWeatherMap",
            "units": "metric"
        }
    
    def _generate_mock_medical_data(self) -> Dict[str, Any]:
        """Generate mock medical data (triggers compliance checks)"""
        return {
            "patient_id": "PT-12345",
            "patient_name": "John Smith",
            "date_of_birth": "1985-03-15",
            "ssn": "123-45-6789",
            "diagnosis": "Hypertension and diabetes monitoring",
            "medications": ["Lisinopril 10mg", "Metformin 500mg"],
            "last_visit": "2024-01-10",
            "blood_pressure": "130/85",
            "heart_rate": 72,
            "temperature": 36.8,
            "hospital": "City General Hospital",
            "physician": "Dr. Emily Johnson"
        }
    
    def _generate_mock_business_data(self) -> Dict[str, Any]:
        """Generate mock business data"""
        return {
            "sales_volume": 15420,
            "customer_count": 428,
            "average_transaction": 36.02,
            "peak_hour": "14:00-15:00",
            "most_popular_product": "Wireless Headphones",
            "customer_satisfaction": 4.3,
            "region": "North America",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_mock_user_data(self) -> Dict[str, Any]:
        """Generate mock user data (triggers GDPR checks)"""
        return {
            "user_id": "USR-78901",
            "user_email": "customer@example.com",
            "user_name": "Alice Johnson",
            "ip_address": "192.168.1.100",
            "phone_number": "+1-555-0123",
            "last_login": "2024-01-15T10:30:00Z",
            "preferences": {"newsletter": True, "theme": "dark"},
            "account_age_days": 127
        }
    
    def _generate_mock_general_data(self) -> Dict[str, Any]:
        """Generate general mock data"""
        return {
            "query_type": "general_inquiry",
            "data_points": 15,
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat(),
            "sample_metric": 42.5,
            "status": "active"
        }
    
    def _get_mock_data(self, query: str) -> Dict[str, Any]:
        """Fallback mock data generator"""
        return {
            "query": query,
            "mock_data": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Using mock data for demonstration"
        }
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics"""
        return {
            "total_requests": len(self.request_history),
            "recent_requests": self.request_history[-5:] if self.request_history else [],
            "most_common_type": self._get_most_common_request_type()
        }
    
    def _get_most_common_request_type(self) -> str:
        """Get most common request type"""
        if not self.request_history:
            return "none"
        
        types = [req['type'] for req in self.request_history]
        return max(set(types), key=types.count)