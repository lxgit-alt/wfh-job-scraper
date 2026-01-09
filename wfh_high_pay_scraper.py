import requests
from bs4 import BeautifulSoup
import random
import re
import time

# --- CONFIGURATION ---
KEYWORDS = ["customer support", "AI writing", "Outlier", "DataAnnotation", "Data Entry"]
MIN_HOURLY = 10.0
MAX_HOURLY = 40.0

def parse_hourly_rate(text):
    """Extracts hourly numbers from strings like '$25/hr' or 'Up to $40 per hour'"""
    # Fix: Remove commas before regex to handle numbers like 50,000
    clean_text = text.replace(',', '')
    matches = re.findall(r'\$?(\d+(?:\.\d+)?)', clean_text)
    
    if not matches:
        return None
    
    text_lower = text.lower()
    val = float(matches[0])
    
    if any(x in text_lower for x in ["hour", "/hr", "hrly"]):
        return val
    elif "year" in text_lower or "annually" in text_lower:
        if val > 1000: 
            return val / 2000  # Convert annual to hourly
    return val

# --- NEW CODE TO "ACCESS" THE LIBRARIES ---

def fetch_jobs(url):
    """
    This function uses requests, BeautifulSoup, and random
    to clear the 'not accessed' warnings.
    """
    # Use 'random' to pick a random delay (mimics human behavior)
    delay = random.uniform(1, 3)
    time.sleep(delay)

    # Use 'requests' to get the webpage
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        
        # Use 'BeautifulSoup' to parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"Success! Accessed: {soup.title.string if soup.title else url}")
        return soup

    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.google.com"
    fetch_jobs(test_url)