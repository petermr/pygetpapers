# Pygetpapers Streamlit UI

A modern web interface for pygetpapers, making scholarly paper discovery and download accessible to all users.

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pygetpapers installed and accessible
- Internet connection for repository access

### Installation

1. **Install pygetpapers** (if not already installed):
   ```bash
   pip install pygetpapers
   ```

2. **Install Streamlit UI dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application**:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 🎯 Features

### 🔍 Search Papers
- **Multi-repository support**: Europe PMC, arXiv, Crossref, OpenAlex, bioRxiv, medRxiv, Rxivist
- **Complex query building**: Boolean operators, field-specific searches, nested quoting
- **Date range filtering**: Time-based searches for supported repositories
- **Multiple download formats**: XML, PDF, supplementary files, references, citations
- **Metadata export**: CSV and HTML formats

### 🔧 Query Builder
- **Visual query construction**: Build complex Boolean queries step-by-step
- **Field-specific searches**: Title, abstract, author, journal, license, methods
- **Real-time preview**: See your query as you build it
- **Query examples**: Learn from provided examples and syntax

### 📁 Corpus Manager
- **Visual corpus management**: Organize and track downloaded papers
- **Analytics dashboard**: Repository distribution and temporal analysis
- **Statistics tracking**: Monitor your research progress
- **Corpus metadata**: View creation details and search parameters

### ⚙️ Settings
- **Default configurations**: Set preferred repositories and limits
- **Performance tuning**: Adjust timeouts and log levels
- **Output customization**: Configure directory patterns and auto-save

### ❓ Help & Documentation
- **Comprehensive guides**: Quick start, troubleshooting, best practices
- **Repository information**: Feature comparison and usage tips
- **Query syntax guide**: Learn advanced search techniques

## 📚 Repository Support

| Repository | Query Support | Date Range | PDF Download | XML Download | References | Citations | Supplementary Files |
|------------|---------------|------------|--------------|--------------|------------|-----------|-------------------|
| Europe PMC | ✅ Full | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| arXiv | ✅ Full | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crossref | ✅ Full | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| OpenAlex | ✅ Full | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| bioRxiv | ❌ (Date only) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| medRxiv | ❌ (Date only) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Rxivist | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## 🔍 Query Examples

### Simple Queries
```bash
"artificial intelligence"
"machine learning" AND "deep learning"
```

### Complex Boolean Queries
```bash
"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'"
"cancer" AND ("treatment" OR "therapy") AND NOT "review"
```

### Field-Specific Queries
```bash
TITLE:"neural networks" AND ABSTRACT:"deep learning"
AUTH:"Smith J" AND JOURNAL:"Nature"
```

### Date Range Queries (Europe PMC)
```bash
"covid-19" AND FIRST_PDATE:[2020-01-01 TO 2023-12-31]
```

## 🏗️ Architecture

The Streamlit UI is built with a modular architecture:

```
pygetpapers/
├── streamlit_app.py          # Main Streamlit application
├── docs/                     # Documentation directory
│   ├── project-overview.md   # Project overview and goals
│   ├── streamlit-ui-implementation.md  # Technical implementation details
│   └── user-guide.md         # Comprehensive user guide
└── requirements.txt          # Updated dependencies
```

### Core Components

1. **PygetpapersUI Class**: Main application orchestrator
2. **Page-based Navigation**: Modular design with separate pages
3. **Session State Management**: Persistent state across interactions
4. **Command Execution**: Subprocess integration with pygetpapers CLI
5. **Error Handling**: Comprehensive error management and user feedback

## 🎨 User Interface

### Design Principles
- **Intuitive navigation**: Clear page structure and sidebar navigation
- **Visual feedback**: Progress indicators, status messages, and analytics
- **Responsive layout**: Optimized for different screen sizes
- **Professional styling**: Custom CSS for modern appearance

### Key Features
- **Wide layout**: Maximizes screen real estate
- **Column-based design**: Efficient use of space
- **Expandable sections**: Reduces visual clutter
- **Emoji icons**: Intuitive visual navigation

## 🔧 Technical Details

### Command Execution
The UI executes pygetpapers commands using Python's `subprocess` module with:
- 5-minute timeout for long-running operations
- Comprehensive error handling
- Real-time progress tracking
- Detailed output capture

### Query Building
Complex queries are constructed from user input parts with:
- Field-specific search support
- Boolean operator handling
- Proper quote escaping
- Real-time validation

### Session Management
Streamlit's session state maintains:
- User preferences and settings
- Corpus metadata and statistics
- Query history and configurations
- Application state across page interactions

## 🚀 Usage Examples

### Basic Search
1. Select "Europe PMC" repository
2. Enter query: `"machine learning"`
3. Set limit to 100 papers
4. Enable XML and CSV download
5. Click "Search and Download"

### Complex Query Building
1. Go to Query Builder page
2. Add query part: `TITLE:"cancer"`
3. Add second part with AND operator: `ABSTRACT:"treatment"`
4. Add third part with OR operator: `ABSTRACT:"therapy"`
5. Copy query to Search page and execute

### Corpus Analysis
1. Download papers from multiple repositories
2. Go to Corpus Manager page
3. View repository distribution chart
4. Analyze temporal download patterns
5. Track total papers and corpora

## 🛠️ Development

### Local Development
```bash
# Clone the repository
git clone https://github.com/petermr/pygetpapers.git
cd pygetpapers

# Switch to v20 branch
git checkout v20

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run streamlit_app.py --server.port 8501 --server.address localhost
```

### Testing
```bash
# Test pygetpapers installation
pygetpapers --help

# Test Streamlit UI
streamlit run streamlit_app.py
```

### Customization
- Modify `streamlit_app.py` for UI changes
- Update `docs/` files for documentation changes
- Adjust CSS styling in the app for visual modifications

## 📖 Documentation

### User Documentation
- **[User Guide](docs/user-guide.md)**: Comprehensive usage instructions
- **[Project Overview](docs/project-overview.md)**: Project goals and architecture
- **[Implementation Guide](docs/streamlit-ui-implementation.md)**: Technical details

### API Documentation
- **[pygetpapers CLI](https://pygetpapers.readthedocs.io/)**: Original CLI documentation
- **[Streamlit Documentation](https://docs.streamlit.io/)**: Streamlit framework docs

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings for all functions
- Include type hints where appropriate

### Testing
- Test with different repositories
- Verify error handling
- Check UI responsiveness
- Validate query building functionality

## 🐛 Troubleshooting

### Common Issues

**"pygetpapers command not found"**
```bash
pip install pygetpapers
# or
pip install git+https://github.com/petermr/pygetpapers.git
```

**"Streamlit not found"**
```bash
pip install streamlit
```

**"Command timed out"**
- Reduce result limit
- Check internet connection
- Try simpler query

**"No results found"**
- Verify query syntax
- Check repository content
- Use broader terms

### Getting Help
- Check the Help page within the application
- Review the [User Guide](docs/user-guide.md)
- Consult [pygetpapers documentation](https://pygetpapers.readthedocs.io/)
- Open an issue on GitHub

## 📈 Performance

### Optimization Tips
- Use appropriate result limits
- Avoid overly complex queries
- Monitor system resources during large downloads
- Plan searches to avoid redundant downloads

### System Requirements
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 1GB free space minimum
- **Network**: Stable internet connection
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## 🔮 Future Enhancements

### Planned Features
1. **Advanced Analytics**: More sophisticated corpus analysis
2. **Batch Operations**: Multiple query execution
3. **Export Options**: Additional output formats
4. **User Authentication**: Multi-user support
5. **API Integration**: Direct API access for advanced users

### Technical Improvements
1. **Async Operations**: Non-blocking command execution
2. **Caching Layer**: Improved performance for repeated operations
3. **Plugin System**: Extensible architecture for new features
4. **Database Integration**: Persistent storage for corpora
5. **Real-time Updates**: WebSocket-based progress tracking

## 📄 License

This project is licensed under the same license as pygetpapers. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **pygetpapers team**: For the excellent CLI tool that makes this possible
- **Streamlit team**: For the powerful web framework
- **OpenVirus community**: For inspiration and feedback
- **Contributors**: All those who help improve this project

## 📞 Support

- **Documentation**: [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/petermr/pygetpapers/issues)
- **Discussions**: [GitHub Discussions](https://github.com/petermr/pygetpapers/discussions)
- **Email**: Contact the pygetpapers maintainers

---

**Happy paper hunting! 📚🔍** 