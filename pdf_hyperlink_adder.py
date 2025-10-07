#!/usr/bin/env python3
"""
PDF Hyperlink Adder

This script adds hyperlinks and visual cues to a PDF based on a word list.
It processes a large PDF (e.g., 350 pages) and adds blue underlined text with tooltips
for each matching word from the provided list.

Requirements:
    pip install PyMuPDF pdfplumber

Usage:
    python pdf_hyperlink_adder.py input.pdf word_list.csv output.pdf
"""

import fitz  # PyMuPDF
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class PDFHyperlinkAdder:
    def __init__(self, input_pdf: str, word_list_file: str, output_pdf: str):
        self.input_pdf = input_pdf
        self.word_list_file = word_list_file
        self.output_pdf = output_pdf
        self.word_links: Dict[str, str] = {}
        self.processed_words = 0
        self.total_matches = 0
        
    def load_word_list(self) -> None:
        """Load the word list with hyperlinks from CSV file"""
        print(f"📖 Loading word list from {self.word_list_file}...")
        
        with open(self.word_list_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    word = row[0].strip().lower()
                    link = row[1].strip()
                    self.word_links[word] = link
                    
        print(f"✅ Loaded {len(self.word_links)} words with hyperlinks")
        
    def find_word_instances(self, doc: fitz.Document) -> List[Tuple[int, str, fitz.Rect, str]]:
        """Find all instances of words in the PDF with their positions"""
        print("🔍 Searching for word instances...")
        
        word_instances = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks with positioning
            text_dict = page.get_text("dict")
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            bbox = fitz.Rect(span["bbox"])
                            
                            # Check each word in our list
                            for word, link in self.word_links.items():
                                # Use case-insensitive search
                                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                                matches = pattern.finditer(text)
                                
                                for match in matches:
                                    # Calculate position of this specific word
                                    start_pos = match.start()
                                    end_pos = match.end()
                                    
                                    # Calculate the bbox for this specific word
                                    char_width = bbox.width / len(text)
                                    word_bbox = fitz.Rect(
                                        bbox.x0 + start_pos * char_width,
                                        bbox.y0,
                                        bbox.x0 + end_pos * char_width,
                                        bbox.y1
                                    )
                                    
                                    word_instances.append((page_num, word, word_bbox, link))
                                    self.total_matches += 1
                                    
        print(f"✅ Found {self.total_matches} word instances across {len(doc)} pages")
        return word_instances
    
    def add_hyperlinks_and_styling(self, doc: fitz.Document, word_instances: List[Tuple[int, str, fitz.Rect, str]]) -> None:
        """Add hyperlinks and visual styling to the PDF"""
        print("🎨 Adding hyperlinks and styling...")
        
        for page_num, word, bbox, link in word_instances:
            page = doc[page_num]
            
            # Add hyperlink annotation
            link_annot = page.insert_link({"kind": fitz.LINK_URI, "uri": link, "from": bbox})
            
            # Add tooltip (using annotation title)
            # Note: PyMuPDF doesn't support tooltips directly, but we can add a text annotation
            tooltip_rect = fitz.Rect(bbox.x0, bbox.y0 - 20, bbox.x1, bbox.y0)
            page.add_text_annot(tooltip_rect.tl, f"Click to visit: {word}")
            
            # Add visual styling - blue underline
            # Note: PyMuPDF doesn't directly modify text color, but we can add visual indicators
            # We'll add a small blue rectangle under the text as a visual cue
            underline_rect = fitz.Rect(bbox.x0, bbox.y1 - 1, bbox.x1, bbox.y1)
            page.draw_rect(underline_rect, color=(0, 0, 1), width=1)  # Blue underline
            
            self.processed_words += 1
            
            if self.processed_words % 100 == 0:
                print(f"   Processed {self.processed_words}/{self.total_matches} words...")
    
    def process_pdf(self) -> None:
        """Main processing function"""
        print(f"📄 Processing PDF: {self.input_pdf}")
        print(f"📝 Word list: {self.word_list_file}")
        print(f"💾 Output: {self.output_pdf}")
        print("-" * 50)
        
        # Load word list
        self.load_word_list()
        
        # Open PDF
        doc = fitz.open(self.input_pdf)
        print(f"📖 PDF opened: {len(doc)} pages")
        
        # Find all word instances
        word_instances = self.find_word_instances(doc)
        
        if not word_instances:
            print("❌ No matching words found in the PDF")
            return
        
        # Add hyperlinks and styling
        self.add_hyperlinks_and_styling(doc, word_instances)
        
        # Save the modified PDF
        doc.save(self.output_pdf)
        doc.close()
        
        print("-" * 50)
        print(f"✅ Processing complete!")
        print(f"📊 Statistics:")
        print(f"   Total words processed: {self.processed_words}")
        print(f"   Total matches found: {self.total_matches}")
        print(f"   Output saved to: {self.output_pdf}")

def create_sample_word_list(filename: str = "word_list.csv") -> None:
    """Create a sample word list CSV file for testing"""
    sample_words = [
        ["python", "https://python.org"],
        ["programming", "https://en.wikipedia.org/wiki/Programming"],
        ["algorithm", "https://en.wikipedia.org/wiki/Algorithm"],
        ["database", "https://en.wikipedia.org/wiki/Database"],
        ["machine learning", "https://en.wikipedia.org/wiki/Machine_learning"],
        ["artificial intelligence", "https://en.wikipedia.org/wiki/Artificial_intelligence"],
        ["data science", "https://en.wikipedia.org/wiki/Data_science"],
        ["web development", "https://en.wikipedia.org/wiki/Web_development"],
        ["cloud computing", "https://en.wikipedia.org/wiki/Cloud_computing"],
        ["cybersecurity", "https://en.wikipedia.org/wiki/Computer_security"]
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["word", "hyperlink"])
        writer.writerows(sample_words)
    
    print(f"📝 Created sample word list: {filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_hyperlink_adder.py input.pdf word_list.csv output.pdf")
        print("\nExample:")
        print("  python pdf_hyperlink_adder.py document.pdf word_list.csv document_with_links.pdf")
        print("\nTo create a sample word list:")
        print("  python pdf_hyperlink_adder.py --create-sample")
        return
    
    if sys.argv[1] == "--create-sample":
        create_sample_word_list()
        return
    
    if len(sys.argv) != 4:
        print("Usage: python pdf_hyperlink_adder.py input.pdf word_list.csv output.pdf")
        print("\nExample:")
        print("  python pdf_hyperlink_adder.py document.pdf word_list.csv document_with_links.pdf")
        print("\nTo create a sample word list:")
        print("  python pdf_hyperlink_adder.py --create-sample")
        return
    
    input_pdf = sys.argv[1]
    word_list_file = sys.argv[2]
    output_pdf = sys.argv[3]
    
    # Check if files exist
    if not Path(input_pdf).exists():
        print(f"❌ Input PDF not found: {input_pdf}")
        return
    
    if not Path(word_list_file).exists():
        print(f"❌ Word list file not found: {word_list_file}")
        return
    
    # Process the PDF
    adder = PDFHyperlinkAdder(input_pdf, word_list_file, output_pdf)
    adder.process_pdf()

if __name__ == "__main__":
    main() 