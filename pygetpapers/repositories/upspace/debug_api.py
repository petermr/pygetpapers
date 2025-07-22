#!/usr/bin/env python3
"""
Debug script to test UPSpace API directly.
"""

import json
import requests
from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


def debug_api():
    """Debug the UPSpace API calls."""
    
    print("=" * 60)
    print("UPSpace API Debug")
    print("=" * 60)
    
    upspace = UPSpace()
    
    # Test 1: Direct API call to search endpoint
    print("\n1. Testing direct API call...")
    search_url = "https://repository.up.ac.za/server/api/discover/search/objects"
    params = {
        "dsoType": "ITEM",
        "sort": "dc.date.accessioned,DESC",
        "page": 0,
        "size": 5,
        "query": "sustainable"
    }
    
    print(f"URL: {search_url}")
    print(f"Params: {params}")
    
    try:
        response = upspace._make_request(search_url, params)
        if response:
            print(f"✓ Response status: {response.status_code}")
            print(f"✓ Response headers: {dict(response.headers)}")
            
            data = response.json()
            print(f"✓ Response data keys: {list(data.keys())}")
            
            if "page" in data:
                results = data["page"]
                print(f"✓ Found {len(results)} results in page")
                
                if results:
                    print("\nFirst result structure:")
                    first_result = results[0]
                    print(f"  Keys: {list(first_result.keys())}")
                    
                    if "_links" in first_result:
                        links = first_result["_links"]
                        print(f"  Links: {list(links.keys())}")
                        
                        if "indexableObject" in links:
                            item_url = links["indexableObject"]["href"]
                            print(f"  Item URL: {item_url}")
                            
                            # Test getting the full item
                            print("\n2. Testing item retrieval...")
                            item_response = upspace._make_request(item_url)
                            if item_response:
                                item_data = item_response.json()
                                print(f"✓ Item retrieved successfully")
                                print(f"✓ Item keys: {list(item_data.keys())}")
                                
                                if "metadata" in item_data:
                                    metadata = item_data["metadata"]
                                    print(f"✓ Metadata fields: {list(metadata.keys())}")
                                    
                                    # Show some sample metadata
                                    if "dc.title" in metadata:
                                        title = metadata["dc.title"][0]["value"]
                                        print(f"✓ Title: {title}")
                                    
                                    if "dc.description.sdg" in metadata:
                                        sdgs = [item["value"] for item in metadata["dc.description.sdg"]]
                                        print(f"✓ SDGs: {sdgs}")
                            else:
                                print("✗ Failed to retrieve item")
                        else:
                            print("✗ No indexableObject link found")
                    else:
                        print("✗ No _links found in result")
                else:
                    print("✗ No results found in page")
            else:
                print("✗ No 'page' key in response")
                print(f"Response content: {data}")
        else:
            print("✗ No response received")
            
    except Exception as e:
        print(f"✗ API call failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_api() 