#!/usr/bin/env python3
"""
Debug script to see exactly what text content is available on Redalyc article pages.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def debug_title_extraction():
    """Debug title extraction on Redalyc article page."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        article_url = "https://www.redalyc.org/articulo.oa?id=66914279011"
        print(f"Navigating to article: {article_url}")
        
        driver.get(article_url)
        time.sleep(5)
        
        print(f"Page title: {driver.title}")
        
        # Get all text content
        page_source = driver.page_source
        text_content = re.sub(r'<[^>]+>', '', page_source)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        print(f"\n=== FULL TEXT CONTENT ===")
        print(text_content[:2000])  # First 2000 chars
        
        print(f"\n=== LOOKING FOR TITLE PATTERNS ===")
        
        # Try the same patterns as in the RedalycSelenium class
        title_patterns = [
            r'([A-Z][A-Z\s\-\.,]+(?:LIPPIA|LANTANA|VERBENACEAE)[A-Z\s\-\.,]*)',
            r'([A-Z][A-Z\s\-\.,]{20,})',
            r'([A-Z][a-z\s\-\.,]{10,})',
        ]
        
        for i, pattern in enumerate(title_patterns):
            print(f"\nPattern {i+1}: {pattern}")
            matches = re.findall(pattern, text_content)
            for j, match in enumerate(matches):
                title_text = match.strip()
                print(f"  Match {j+1}: '{title_text}'")
                if (title_text and 
                    len(title_text) > 10 and 
                    'redalyc' not in title_text.lower() and
                    'sistema' not in title_text.lower() and
                    'información' not in title_text.lower() and
                    'científica' not in title_text.lower()):
                    print(f"    -> VALID TITLE CANDIDATE!")
                else:
                    print(f"    -> REJECTED (filtered out)")
        
        # Look for specific text we know should be there
        print(f"\n=== LOOKING FOR KNOWN TEXT ===")
        known_texts = [
            "NOVEDADES NOMENCLATURALES",
            "LIPPIA",
            "LANTANA", 
            "VERBENACEAE"
        ]
        
        for text in known_texts:
            if text in text_content:
                print(f"Found '{text}' in content")
            else:
                print(f"NOT found '{text}' in content")
        
    except Exception as e:
        print(f"Error during debug: {e}")
    
    finally:
        driver.quit()
        print("\nDebug complete!")

if __name__ == "__main__":
    debug_title_extraction() 