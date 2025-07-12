#!/usr/bin/env python3
"""
Script to investigate Redalyc's search form structure.
This will help us find the correct selectors for the search box and form.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def investigate_redalyc_search():
    """Investigate Redalyc's search form structure."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Navigating to Redalyc homepage...")
        driver.get("https://redalyc.org/")
        time.sleep(3)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Look for search forms
        print("\n=== SEARCH FORMS ===")
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Found {len(forms)} forms on the page")
        
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(f"  Action: {form.get_attribute('action')}")
            print(f"  Method: {form.get_attribute('method')}")
            print(f"  ID: {form.get_attribute('id')}")
            print(f"  Class: {form.get_attribute('class')}")
            
            # Look for input fields in this form
            inputs = form.find_elements(By.TAG_NAME, "input")
            print(f"  Input fields: {len(inputs)}")
            for j, inp in enumerate(inputs):
                print(f"    Input {j+1}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}, placeholder={inp.get_attribute('placeholder')}")
        
        # Look for search boxes by common selectors
        print("\n=== SEARCH BOXES ===")
        search_selectors = [
            "input[name='q']",
            "input[name='query']",
            "input[name='search']",
            "input[type='search']",
            "input[placeholder*='search']",
            "input[placeholder*='buscar']",
            "input[placeholder*='Search']",
            "input[placeholder*='Buscar']",
            ".search input",
            "#search input",
            "form input[type='text']"
        ]
        
        for selector in search_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    for elem in elements:
                        print(f"  - type={elem.get_attribute('type')}, name={elem.get_attribute('name')}, id={elem.get_attribute('id')}, placeholder={elem.get_attribute('placeholder')}")
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
        
        # Look for search buttons
        print("\n=== SEARCH BUTTONS ===")
        button_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "button[class*='search']",
            "button[class*='buscar']",
            "input[value*='search']",
            "input[value*='buscar']",
            "input[value*='Search']",
            "input[value*='Buscar']"
        ]
        
        for selector in button_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    for elem in elements:
                        print(f"  - type={elem.get_attribute('type')}, value={elem.get_attribute('value')}, text={elem.text}")
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
        
        # Get page source for manual inspection
        print("\n=== PAGE SOURCE SNIPPET ===")
        page_source = driver.page_source
        # Look for search-related content
        search_indicators = ['search', 'buscar', 'query', 'q=']
        lines = page_source.split('\n')
        for i, line in enumerate(lines):
            if any(indicator in line.lower() for indicator in search_indicators):
                print(f"Line {i+1}: {line.strip()}")
                if i > 10:  # Limit output
                    break
        
    except Exception as e:
        print(f"Error during investigation: {e}")
    
    finally:
        driver.quit()
        print("\nInvestigation complete!")

if __name__ == "__main__":
    investigate_redalyc_search() 