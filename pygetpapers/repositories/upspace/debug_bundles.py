#!/usr/bin/env python3
"""
Debug script to test UPSpace bundles API.
"""

import json
from pathlib import Path

from pygetpapers.repositories.upspace.upspace import UPSpace


def debug_bundles():
    """Debug the UPSpace bundles API calls."""
    
    print("=" * 60)
    print("UPSpace Bundles API Debug")
    print("=" * 60)
    
    upspace = UPSpace()
    
    # First, get a sample article
    articles = upspace.search_articles("sustainable", 1)
    if not articles:
        print("No articles found")
        return
    
    article = articles[0]
    print(f"Testing with article: {article.get('title', 'No title')}")
    print(f"UUID: {article.get('uuid')}")
    
    # Test bundles API
    print("\n1. Testing bundles API...")
    bundles_data = upspace._get_item_bundles(article["uuid"])
    
    if bundles_data:
        print(f"✓ Bundles data type: {type(bundles_data)}")
        print(f"✓ Bundles data keys: {list(bundles_data.keys()) if isinstance(bundles_data, dict) else 'Not a dict'}")
        
        if isinstance(bundles_data, dict):
            print(f"✓ Full bundles data structure:")
            print(f"  _embedded keys: {list(bundles_data.get('_embedded', {}).keys())}")
            print(f"  page keys: {list(bundles_data.get('page', {}).keys())}")
            
            # Check _embedded for bundles
            if "_embedded" in bundles_data:
                embedded_bundles = bundles_data["_embedded"]
                print(f"✓ Embedded bundles keys: {list(embedded_bundles.keys())}")
                
                if "bundles" in embedded_bundles:
                    bundles = embedded_bundles["bundles"]
                    print(f"✓ Found {len(bundles)} bundles in _embedded.bundles")
                    
                    for i, bundle in enumerate(bundles):
                        print(f"  Bundle {i+1}:")
                        print(f"    Type: {type(bundle)}")
                        print(f"    Value: {bundle}")
                        
                        if isinstance(bundle, dict):
                            print(f"    Name: {bundle.get('name')}")
                            print(f"    UUID: {bundle.get('uuid')}")
                            print(f"    Type: {bundle.get('type')}")
                            
                            # Test bitstreams for this bundle
                            if bundle.get('name') == 'ORIGINAL':
                                print(f"\n2. Testing bitstreams for ORIGINAL bundle...")
                                bitstreams_data = upspace._get_bundle_bitstreams(bundle['uuid'])
                                
                                if bitstreams_data:
                                    print(f"✓ Bitstreams data type: {type(bitstreams_data)}")
                                    print(f"✓ Bitstreams data keys: {list(bitstreams_data.keys()) if isinstance(bitstreams_data, dict) else 'Not a dict'}")
                                    
                                    if isinstance(bitstreams_data, dict):
                                        print(f"✓ Full bitstreams data structure:")
                                        print(f"  _embedded keys: {list(bitstreams_data.get('_embedded', {}).keys())}")
                                        print(f"  page keys: {list(bitstreams_data.get('page', {}).keys())}")
                                        
                                        # Check _embedded for bitstreams
                                        if "_embedded" in bitstreams_data and "bitstreams" in bitstreams_data["_embedded"]:
                                            bitstreams = bitstreams_data["_embedded"]["bitstreams"]
                                            print(f"✓ Found {len(bitstreams)} bitstreams in _embedded.bitstreams")
                                            
                                            for j, bitstream in enumerate(bitstreams):
                                                print(f"  Bitstream {j+1}:")
                                                print(f"    Type: {type(bitstream)}")
                                                print(f"    Value: {bitstream}")
                                                
                                                if isinstance(bitstream, dict):
                                                    print(f"    Name: {bitstream.get('name')}")
                                                    print(f"    UUID: {bitstream.get('uuid')}")
                                                    print(f"    Size: {bitstream.get('sizeBytes')}")
                                                    print(f"    Format: {bitstream.get('format')}")
                                else:
                                    print("✗ No bitstreams data received")
                        else:
                            print(f"    (Unknown type: {type(bundle)})")
                else:
                    print("✗ No 'bundles' key in _embedded")
            else:
                print("✗ No '_embedded' key in bundles data")
        else:
            print(f"✗ Bundles data is not a dictionary: {bundles_data}")
    else:
        print("✗ No bundles data received")


if __name__ == "__main__":
    debug_bundles() 