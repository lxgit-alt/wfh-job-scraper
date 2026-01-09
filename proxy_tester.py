import requests
import threading

# The raw URL from TheSpeedX
URL = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"

def check_proxy(proxy):
    try:
        # We test against a simple API that returns your IP address
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get("https://api.ipify.org", proxies=proxies, timeout=5)
        if r.status_code == 200:
            print(f"[WORKING] {proxy}")
            with open("working.txt", "a") as f:
                f.write(proxy + "\n")
    except:
        pass # Proxy is dead or slow

def main():
    print("Downloading proxy list...")
    r = requests.get(URL)
    proxies = r.text.splitlines()
    print(f"Total proxies found: {len(proxies)}. Starting test...")
    
    # Using Threads to make it fast
    for p in proxies:
        t = threading.Thread(target=check_proxy, args=(p,))
        t.start()

if __name__ == "__main__":
    main()