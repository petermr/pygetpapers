#!/usr/bin/env python3
"""
Debug script to see what's actually on a Redalyc article page.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_article_page():
    """Debug a Redalyc article page."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Test with one of the article URLs we found
        article_url = "https://www.redalyc.org/articulo.oa?id=66914279011"
        print(f"Navigating to article: {article_url}")
        
        driver.get(article_url)
        time.sleep(5)  # Wait for page to load
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Check if we got redirected or got an error page
        if "error" in driver.current_url.lower() or "not found" in driver.current_url.lower():
            print("ERROR: Got redirected to error page!")
        
        # Look for common article elements
        print("\n=== LOOKING FOR ARTICLE ELEMENTS ===")
        
        # Title selectors
        title_selectors = ['h1', '.title', '.article-title', 'title', '.titulo', '.titulo-articulo']
        for selector in title_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Title selector '{selector}': Found {len(elements)} elements")
                    for i, elem in enumerate(elements):
                        print(f"  Element {i+1}: '{elem.text.strip()}'")
            except Exception as e:
                print(f"Title selector '{selector}': Error - {e}")
        
        # Author selectors
        author_selectors = ['.authors', '.author', '.author-list', '.autores', '.autor']
        for selector in author_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Author selector '{selector}': Found {len(elements)} elements")
                    for i, elem in enumerate(elements):
                        print(f"  Element {i+1}: '{elem.text.strip()}'")
            except Exception as e:
                print(f"Author selector '{selector}': Error - {e}")
        
        # Abstract selectors
        abstract_selectors = ['.abstract', '.resumen', '.summary', '.abstract-text', '.resumen-texto']
        for selector in abstract_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Abstract selector '{selector}': Found {len(elements)} elements")
                    for i, elem in enumerate(elements):
                        print(f"  Element {i+1}: '{elem.text.strip()[:100]}...'")
            except Exception as e:
                print(f"Abstract selector '{selector}': Error - {e}")
        
        # Check page source for content
        print("\n=== PAGE SOURCE ANALYSIS ===")
        page_source = driver.page_source
        
        # Look for common text patterns
        if "This browser is no longer supported" in page_source:
            print("WARNING: Found 'This browser is no longer supported' message")
        
        if "error" in page_source.lower():
            print("WARNING: Found 'error' in page source")
        
        if "not found" in page_source.lower():
            print("WARNING: Found 'not found' in page source")
        
        # Look for any text content
        import re
        text_content = re.sub(r'<[^>]+>', '', page_source)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        print(f"Page source length: {len(page_source)}")
        print(f"Text content (first 500 chars): {text_content[:500]}")
        
        # Look for any links
        print("\n=== LINKS ON PAGE ===")
        links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"Found {len(links)} links")
        for i, link in enumerate(links[:10]):  # Show first 10
            href = link.get_attribute('href')
            text = link.text.strip()
            if href and text:
                print(f"  Link {i+1}: '{text}' -> {href}")
        
    except Exception as e:
        print(f"Error during debug: {e}")
    
    finally:
        driver.quit()
        print("\nDebug complete!")

if __name__ == "__main__":
    debug_article_page() 