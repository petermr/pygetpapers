#!/usr/bin/env python3
"""
Example usage of the PDF to HTML Converter

This script demonstrates how to use the PDFToHTMLConverter class
to download PDFs and convert them to well-formatted HTML.
"""

from pathlib import Path

from pdf_to_html_converter import PDFToHTMLConverter


def example_local_pdf():
    """Example: Convert a local PDF file."""
    print("=== Example: Local PDF Conversion ===")

    converter = PDFToHTMLConverter(output_dir="example_output")

    # Replace with path to your PDF file
    pdf_path = Path("example.pdf")

    if pdf_path.exists():
        try:
            html_path = converter.convert_pdf_to_html(pdf_path, "Example Document")
            print(f"✅ Conversion completed!")
            print(f"📄 PDF: {pdf_path}")
            print(f"🌐 HTML: {html_path}")
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
    else:
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please place a PDF file named 'example.pdf' in the current directory.")


def example_download_and_convert():
    """Example: Download PDF from URL and convert."""
    print("\n=== Example: Download and Convert ===")

    converter = PDFToHTMLConverter(output_dir="example_output")

    # Example URL (replace with actual PDF URL)
    url = "https://arxiv.org/pdf/2103.12345.pdf"  # Replace with real URL

    try:
        pdf_path, html_path = converter.download_and_convert(
            url, "Downloaded Research Paper"
        )
        print(f"✅ Download and conversion completed!")
        print(f"📥 Downloaded PDF: {pdf_path}")
        print(f"🌐 Generated HTML: {html_path}")
    except Exception as e:
        print(f"❌ Download/conversion failed: {e}")
        print("Please provide a valid PDF URL.")


def example_batch_processing():
    """Example: Process multiple PDF files in a directory."""
    print("\n=== Example: Batch Processing ===")

    converter = PDFToHTMLConverter(output_dir="batch_output")

    # Directory containing PDF files
    pdf_dir = Path("pdfs")

    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if pdf_files:
            print(f"Found {len(pdf_files)} PDF files to process:")

            for pdf_file in pdf_files:
                try:
                    print(f"\nProcessing: {pdf_file.name}")
                    html_path = converter.convert_pdf_to_html(pdf_file)
                    print(f"✅ Converted: {html_path.name}")
                except Exception as e:
                    print(f"❌ Failed to convert {pdf_file.name}: {e}")
        else:
            print("No PDF files found in the 'pdfs' directory.")
    else:
        print(
            "Directory 'pdfs' not found. Create it and add PDF files for batch processing."
        )


def example_custom_processing():
    """Example: Custom processing with specific settings."""
    print("\n=== Example: Custom Processing ===")

    # Create converter with custom output directory
    converter = PDFToHTMLConverter(output_dir="custom_output")

    # Example: Process a PDF with custom title
    pdf_path = Path("research_paper.pdf")

    if pdf_path.exists():
        try:
            # Convert with custom title
            html_path = converter.convert_pdf_to_html(
                pdf_path, title="Advanced Machine Learning Research Paper"
            )

            print(f"✅ Custom conversion completed!")
            print(f"📄 Input: {pdf_path}")
            print(f"🌐 Output: {html_path}")

            # Show the generated HTML file size
            if html_path.exists():
                size_kb = html_path.stat().st_size / 1024
                print(f"📊 HTML file size: {size_kb:.1f} KB")

        except Exception as e:
            print(f"❌ Custom conversion failed: {e}")
    else:
        print(f"❌ PDF file not found: {pdf_path}")


def main():
    """Run all examples."""
    print("🚀 PDF to HTML Converter Examples")
    print("=" * 50)

    # Run examples
    example_local_pdf()
    example_download_and_convert()
    example_batch_processing()
    example_custom_processing()

    print("\n" + "=" * 50)
    print("📚 Usage Summary:")
    print("1. For local PDF: converter.convert_pdf_to_html(pdf_path)")
    print("2. For URL download: converter.download_and_convert(url)")
    print("3. For batch processing: Process multiple files in a loop")
    print("4. Custom output directory: PDFToHTMLConverter(output_dir='my_dir')")

    print("\n💡 Tips:")
    print("- The converter automatically handles line joining and paragraph creation")
    print("- Section titles are automatically detected and formatted")
    print("- Generated HTML includes CSS styling for better readability")
    print("- All files are saved in the specified output directory")


if __name__ == "__main__":
    main()
