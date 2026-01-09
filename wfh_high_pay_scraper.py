import os
import time
import re
import csv
from playwright.sync_api import sync_playwright

# --- CONFIG ---
TARGETS = [
    {"name": "Outlier", "url": "https://outlier.ai/experts/", "button": None},
    {"name": "DataAnnotation", "url": "https://www.dataannotation.tech/", "button": None},
    {"name": "Alignerr", "url": "https://www.alignerr.com/", "button": None},
    {"name": "OneForma", "url": "https://www.oneforma.com/job-opportunities/", "button": "button:has-text('Load More')"},
    {"name": "InvisibleTech", "url": "https://www.invisible.co/careers", "button": None},
    {"name": "Remotive", "url": "https://remotive.com/remote-jobs/software-dev", "button": "button:has-text('Show more')"},
    {"name": "RemoteOK", "url": "https://remoteok.com/remote-engineer-jobs", "button": None},
    {"name": "WorkingNomads", "url": "https://www.workingnomads.com/jobs", "button": "button#load-more"},
    {"name": "WeWorkRemotely", "url": "https://weworkremotely.com/remote-jobs/search?term=ai", "button": "a.view-all"},
    {"name": "DailyRemote", "url": "https://dailyremote.com/remote-ai-jobs", "button": None}
]

MIN_PAY = 10.0
MAX_PAY = 65.0

def parse_salary(text):
    hr_pattern = r'\$?(\d{1,2}(?:\.\d{2})?)\s?(?:/hr|per hour|hourly)'
    yr_pattern = r'\$?(\d{2,3})[kK]'
    hr_match = re.findall(hr_pattern, text, re.IGNORECASE)
    if hr_match:
        val = float(hr_match[0])
        return val if MIN_PAY <= val <= MAX_PAY else None
    yr_match = re.findall(yr_pattern, text)
    if yr_match:
        val = (float(yr_match[0]) * 1000) / 2000
        return val if MIN_PAY <= val <= MAX_PAY else None
    return None

def is_remote(text):
    """Filters for explicit remote keywords."""
    remote_keywords = [r'remote', r'worldwide', r'anywhere', r'wfh', r'work from home', r'distributed']
    pattern = '|'.join(remote_keywords)
    return bool(re.search(pattern, text, re.IGNORECASE))

def run_scraper():
    proxy_server = "http://142.111.48.253:7030"
    proxy_user = os.getenv("PROXY_USER")
    proxy_pass = os.getenv("PROXY_PASS")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": proxy_server, "username": proxy_user, "password": proxy_pass}
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        for target in TARGETS:
            page = context.new_page()
            print(f"📡 Scanning: {target['name']}")
            
            try:
                page.goto(target['url'], wait_until="networkidle", timeout=60000)
                time.sleep(5) 

                if target['button']:
                    try:
                        btn = page.locator(target['button']).first
                        if btn.is_visible(timeout=5000):
                            btn.click()
                            time.sleep(3)
                    except:
                        pass

                page.screenshot(path=f"{target['name']}_jobs.png")

                elements = page.query_selector_all('a, div, span, p')
                seen_jobs = set()

                for el in elements:
                    text = el.inner_text().strip()
                    if not text or len(text) < 10: continue
                    
                    pay_found = parse_salary(text)
                    # New Filter: Must have pay AND mention 'Remote/Worldwide'
                    if pay_found and is_remote(text):
                        job_title = text.split('\n')[0][:70].strip()
                        if job_title not in seen_jobs:
                            results.append({
                                "Site": target['name'],
                                "Job": job_title,
                                "Pay": f"${pay_found:.2f}/hr",
                                "Link": target['url'] 
                            })
                            seen_jobs.add(job_title)
            except Exception as e:
                print(f"❌ Error on {target['name']}: {str(e)[:50]}")
            finally:
                page.close()
        
        browser.close()

    if results:
        with open('wfh_leads.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Site", "Job", "Pay", "Link"])
            writer.writeheader()
            writer.writerows(results)
        print(f"📊 Report Generated: {len(results)} remote jobs found.")

if __name__ == "__main__":
    run_scraper()