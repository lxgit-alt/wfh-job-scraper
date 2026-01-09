import os
import random
import time
import re
import csv
from playwright.sync_api import sync_playwright

# --- CONFIG ---
TARGETS = [
    {"name": "Outlier", "url": "https://outlier.ai/experts/", "button": None}, # Mostly static/scroll
    {"name": "DataAnnotation", "url": "https://www.dataannotation.tech/", "button": None},
    {"name": "Remotive", "url": "https://remotive.com/remote-jobs/customer-support", "button": "button:has-text('Show more')"},
    {"name": "WorkingNomads", "url": "https://www.workingnomads.com/jobs", "button": "button#load-more"},
    {"name": "Alignerr", "url": "https://www.alignerr.com/", "button": None}
]

MIN_PAY = 10.0
MAX_PAY = 50.0

def parse_salary(text):
    """Detects hourly rates like $25/hr or 30 per hour in a string."""
    pattern = r'\$?(\d{1,2}(?:\.\d{2})?)\s?(?:/hr|per hour|hourly)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        try:
            val = float(matches[0])
            if MIN_PAY <= val <= MAX_PAY:
                return val
        except ValueError:
            return None
    return None

def run_scraper():
    # Load Proxies
    try:
        with open("fast_us_proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
            proxy_server = random.choice(proxies)
    except:
        print("No proxies found. Using local IP.")
        proxy_server = None

    results = []

    with sync_playwright() as p:
        browser_args = {}
        if proxy_server:
            browser_args['proxy'] = {"server": f"http://{proxy_server}"}

        browser = p.chromium.launch(headless=True, **browser_args)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0")
        
        for target in TARGETS:
            page = context.new_page()
            print(f"💰 Scanning {target['name']}...")
            
            try:
                page.goto(target['url'], wait_until="networkidle", timeout=60000)
                time.sleep(3)

                # --- AUTO-CLICK LOAD MORE ---
                if target['button']:
                    print(f"🔄 Clicking 'Load More' on {target['name']}...")
                    for _ in range(3): # Click up to 3 times to get more jobs
                        try:
                            # Scroll to button so it's clickable
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            btn = page.locator(target['button'])
                            if btn.is_visible(timeout=5000):
                                btn.click()
                                time.sleep(4) # Wait for new content to load
                            else:
                                break
                        except:
                            break

                # Take Screenshot after loading all jobs
                page.screenshot(path=f"{target['name']}_jobs.png")

                # Parse Jobs
                links = page.query_selector_all('a')
                for link in links:
                    text = link.inner_text()
                    pay_found = parse_salary(text)
                    if pay_found:
                        results.append({
                            "Site": target['name'],
                            "Job": text.split('\n')[0][:50],
                            "Pay": f"${pay_found}/hr",
                            "Link": link.get_attribute('href') or target['url']
                        })

            except Exception as e:
                print(f"Error on {target['name']}: {e}")
            page.close()
        
        browser.close()

    # Save to CSV
    if results:
        with open('wfh_leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Site", "Job", "Pay", "Link"])
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Found {len(results)} matches!")

if __name__ == "__main__":
    run_scraper()