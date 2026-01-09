import requests
import random

# Load the proxies we found earlier
def load_proxies():
    with open("fast_us_proxies.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def scrape_with_rotation(url):
    proxy_pool = load_proxies()
    
    if not proxy_pool:
        print("No proxies found! Run the tester script first.")
        return

    # Try 5 different proxies for the request
    for i in range(5):
        proxy_ip = random.choice(proxy_pool)
        proxies = {
            "http": f"http://{proxy_ip}",
            "https": f"http://{proxy_ip}"
        }
        
        print(f"Attempt {i+1}: Trying proxy {proxy_ip}...")
        
        try:
            # We add a User-Agent to look like a real browser
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, proxies=proxies, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print("Success! Data received.")
                return response.text
        except Exception as e:
            print(f"Proxy {proxy_ip} failed. Swapping...")
    
    print("All attempts failed. The proxies might have died.")

# Test it out
content = scrape_with_rotation("https://httpbin.org/ip")
if content:
    print(f"Final Output: {content}")