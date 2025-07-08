#!/usr/bin/env python3
"""
Test script to verify corpus detection is working
"""

import sys
from pathlib import Path
import json
from datetime import datetime


def test_corpus_detection():
    """Test the corpus detection logic"""

    # Add current directory to path
    sys.path.insert(0, str(Path.cwd()))

    try:
        from streamlit_app import PygetpapersUI

        # Create UI instance
        ui = PygetpapersUI()

        # Test corpus detection
        ui._scan_for_existing_corpora()

        # Check session state (simulate)
        corpora = []
        current_dir = Path.cwd()

        for item in current_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                if ui._is_pygetpapers_output(item):
                    corpus_info = ui._extract_corpus_info(item)
                    if corpus_info:
                        corpora.append(corpus_info)

        print(f"✅ Detected {len(corpora)} corpora:")
        for corpus in corpora:
            if corpus.get("requested_limit", 0) > 0:
                success_rate = (
                    corpus["downloaded_papers"] / corpus["requested_limit"]
                ) * 100
                print(
                    f"  📁 {corpus['name']}: {corpus['downloaded_papers']}/{corpus['requested_limit']} papers ({success_rate:.0f}% success) - {corpus['api']}"
                )
            else:
                print(
                    f"  📁 {corpus['name']}: {corpus['downloaded_papers']} papers ({corpus['api']})"
                )

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Testing corpus detection...")
    success = test_corpus_detection()
    if success:
        print("✅ Corpus detection test passed!")
    else:
        print("❌ Corpus detection test failed!")
