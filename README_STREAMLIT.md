# Pygetpapers Streamlit Web Interface

A comprehensive web interface for pygetpapers with advanced features including query building, corpus management, data visualization, and fulltext search.

## Features

- **Multi-page Interface**: Search Papers, Query Builder, Corpus Manager, Settings, Help
- **Repository Support**: Europe PMC, Crossref, arXiv, OpenAlex, bioRxiv, medRxiv
- **Advanced Query Building**: Boolean logic, date ranges, filters
- **Corpus Management**: Browse, analyze, and manage downloaded papers
- **Data Visualization**: Interactive charts and statistics
- **File Browser**: Universal file browser with directory navigation
- **Progress Tracking**: Real-time download progress with detailed statistics
- **Export Capabilities**: CSV export, data tables, figure galleries

## Installation

### Prerequisites
- Python 3.8 or higher
- pygetpapers installed and working

### Install Dependencies
```bash
pip install streamlit plotly pandas
```

### Run the Application
```bash
streamlit run streamlit_app.py
```

Or use the convenience script:
```bash
python run_streamlit.py
```

The application will start on `http://localhost:8501` (or the next available port).

## Usage

### 1. Search Papers
- Select repository (Europe PMC, arXiv, etc.)
- Enter search query
- Set date range and limits
- Choose download options (XML, PDF, supplementary files)
- Click "Search and Download"

### 2. Query Builder
- Build complex queries with Boolean logic
- Add filters for authors, journals, dates
- Preview and execute queries

### 3. Corpus Manager
- Browse downloaded papers
- View metadata and statistics
- Export data in various formats
- Compare multiple corpora

### 4. File Browser
- Navigate any directory on your system
- View and download files
- Browse corpus contents
- Preview images and text files

### 5. Settings
- Configure default directories
- Set download limits
- Manage application preferences

## Dependencies

The application uses the following key dependencies:
- **streamlit**: Web interface framework
- **plotly**: Interactive data visualization
- **pandas**: Data manipulation and analysis
- **lxml**: XML processing (for JATS4R integration)

All dependencies are properly managed and the application includes comprehensive error handling for missing optional dependencies.

## Troubleshooting

### Common Issues

1. **Port already in use**: The app will automatically find the next available port
2. **Missing dependencies**: Install with `pip install streamlit plotly pandas`
3. **pygetpapers not found**: Ensure pygetpapers is installed and in your PATH

### Getting Help

- Use the "Help" page in the application
- Check the logs for detailed error messages
- Review the pygetpapers documentation for CLI usage

## Development

### Project Structure
```
pygetpapers/
├── streamlit_app.py          # Main Streamlit application
├── run_streamlit.py          # Convenience run script
├── datatables_integration.py # Data table functionality
├── jats4r_integration.py     # XML processing (optional)
└── docs/                     # Documentation
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details. 