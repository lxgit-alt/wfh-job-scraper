import requests
import threading
import time

# Settings
PROXY_LIST_URL = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
GEO_API = "http://ip-api.com/json/"
MAX_LATENCY = 2.0  # Seconds
THREADS = 100

def check_proxy(proxy):
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    try:
        # Start the timer
        start_time = time.time()
        
        # Step 1: Request Geo Data (This acts as our working check + latency test)
        response = requests.get(GEO_API, proxies=proxies, timeout=5)
        
        # Calculate Latency
        latency = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Step 2: Filter by Country (US) AND Speed
            if data.get("countryCode") == "US" and latency <= MAX_LATENCY:
                result = f"[FOUND] {proxy} | Speed: {latency:.2f}s | City: {data.get('city')}"
                print(result)
                
                # Save to file
                with open("fast_us_proxies.txt", "a") as f:
                    f.write(proxy + "\n")
    except:
        pass

def main():
    # Reset result file
    open("fast_us_proxies.txt", "w").close()
    
    print(f"Downloading lists... filtering for US proxies under {MAX_LATENCY}s")
    try:
        raw_data = requests.get(PROXY_LIST_URL).text
        proxies = raw_data.splitlines()
    except Exception as e:
        print(f"Error fetching list: {e}")
        return

    print(f"Scanning {len(proxies)} proxies with {THREADS} threads...")

    # Multi-threading for speed
    threads = []
    for p in proxies:
        t = threading.Thread(target=check_proxy, args=(p,))
        t.daemon = True # Allows script to exit even if threads are running
        t.start()
        threads.append(t)
        
        # Control thread burst so we don't overwhelm your CPU
        if len(threads) >= THREADS:
            for t in threads:
                t.join()
            threads = []

    print("\nScan complete. Check 'fast_us_proxies.txt' for results.")

if __name__ == "__main__":
    main()