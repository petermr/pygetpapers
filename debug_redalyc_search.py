#!/usr/bin/env python3
"""
Debug script to see what's actually on the Redalyc page.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_redalyc():
    """Debug Redalyc page structure."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Navigating to Redalyc homepage...")
        driver.get("https://redalyc.org/")
        time.sleep(5)  # Wait longer for page to load
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Look for the specific search input
        print("\n=== LOOKING FOR SEARCH INPUT ===")
        
        # Try different selectors
        selectors = [
            ("By.NAME", By.NAME, "input-articulo"),
            ("By.ID", By.ID, "input-articulo"),
            ("By.CSS_SELECTOR", By.CSS_SELECTOR, "#input-articulo"),
            ("By.CSS_SELECTOR", By.CSS_SELECTOR, "input[name='input-articulo']"),
            ("By.CSS_SELECTOR", By.CSS_SELECTOR, "input[placeholder*='Buscar']"),
            ("By.CSS_SELECTOR", By.CSS_SELECTOR, "input[type='text']"),
        ]
        
        for desc, by, value in selectors:
            try:
                elements = driver.find_elements(by, value)
                print(f"{desc} '{value}': Found {len(elements)} elements")
                for i, elem in enumerate(elements):
                    print(f"  Element {i+1}:")
                    print(f"    tag: {elem.tag_name}")
                    print(f"    type: {elem.get_attribute('type')}")
                    print(f"    name: {elem.get_attribute('name')}")
                    print(f"    id: {elem.get_attribute('id')}")
                    print(f"    placeholder: {elem.get_attribute('placeholder')}")
                    print(f"    visible: {elem.is_displayed()}")
            except Exception as e:
                print(f"{desc} '{value}': Error - {e}")
        
        # Get all input elements
        print("\n=== ALL INPUT ELEMENTS ===")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Total input elements: {len(all_inputs)}")
        
        for i, inp in enumerate(all_inputs):
            print(f"Input {i+1}:")
            print(f"  type: {inp.get_attribute('type')}")
            print(f"  name: {inp.get_attribute('name')}")
            print(f"  id: {inp.get_attribute('id')}")
            print(f"  placeholder: {inp.get_attribute('placeholder')}")
            print(f"  visible: {inp.is_displayed()}")
            print(f"  value: {inp.get_attribute('value')}")
        
        # Check if page is fully loaded
        print("\n=== PAGE LOAD STATUS ===")
        print(f"Page source length: {len(driver.page_source)}")
        
        # Look for any JavaScript errors or dynamic content
        print("\n=== JAVASCRIPT CONSOLE ===")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"Log: {log}")
        
    except Exception as e:
        print(f"Error during debug: {e}")
    
    finally:
        driver.quit()
        print("\nDebug complete!")

if __name__ == "__main__":
    debug_redalyc() 