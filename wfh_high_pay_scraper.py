import os
import random
import time
from playwright.sync_api import sync_playwright

# --- CONFIG ---
TARGETS = [
    {"name": "Outlier", "url": "https://outlier.ai/experts/"},
    {"name": "DataAnnotation", "url": "https://www.dataannotation.tech/"},
    {"name": "Remotive", "url": "https://remotive.com/remote-jobs/customer-support"},
    {"name": "WorkingNomads", "url": "https://www.workingnomads.com/jobs?category=customer-support"},
    {"name": "Alignerr", "url": "https://www.alignerr.com/"}
]

def get_proxy():
    try:
        with open("fast_us_proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
            return random.choice(proxies) if proxies else None
    except: return None

def run_scraper():
    proxy_server = get_proxy()
    if not proxy_server:
        print("No US proxies found! Run proxy tester first.")
        return

    with sync_playwright() as p:
        # Launch browser with US Proxy to bypass geo-blocks
        browser = p.chromium.launch(headless=True, proxy={"server": f"http://{proxy_server}"})
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        for target in TARGETS:
            page = context.new_page()
            print(f"Checking {target['name']}...")
            
            try:
                # Navigate and wait for content
                page.goto(target['url'], wait_until="networkidle", timeout=60000)
                time.sleep(5) # Extra wait for JS elements
                
                # Take the screenshot for Discord proof
                screenshot_path = f"{target['name']}_jobs.png"
                page.screenshot(path=screenshot_path, full_page=False)
                print(f"✅ Captured {target['name']}")
                
            except Exception as e:
                print(f"❌ Failed {target['name']}: {e}")
            finally:
                page.close()
        
        browser.close()

if __name__ == "__main__":
    run_scraper()