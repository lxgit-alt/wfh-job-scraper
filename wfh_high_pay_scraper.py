import requests
from bs4 import BeautifulSoup
import random
import re

# --- CONFIGURATION ---
KEYWORDS = ["customer support", "AI writing", "Outlier", "DataAnnotation", "Data Entry"]
MIN_HOURLY = 10.0
MAX_HOURLY = 40.0

def parse_hourly_rate(text):
    """Extracts hourly numbers from strings like '$25/hr' or 'Up to $40 per hour'"""
    # Look for patterns like $25, 25/hr, 25 per hour
    matches = re.findall(r'\$?(\d+(?:\.\d+)?)', text)
    if not matches:
        return None
    
    # Check if the context is hourly
    text_lower = text.lower()
    if "hour" in text_lower or "/hr" in text_lower or "hrly" in text_lower:
        val = float(matches[0])
        # If it's a range like 15-25, matches[0] is 15. We'll take the first number.
        return val
    
    # If it's a yearly salary (e.g. 50,000), convert to hourly (~2000 hours/year)
    elif "year" in text_lower or "annually" in text_lower:
        val = float(matches[0].replace(',', ''))
        if val > 1000: # Sanity check for yearly
            return val