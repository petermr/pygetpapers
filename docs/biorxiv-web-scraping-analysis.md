# BioRxiv Web Scraping Analysis

## Overview

This document analyzes the potential for implementing web scraping functionality for bioRxiv's search interface to provide text-based search capabilities, complementing the existing API-based date-only search in pygetpapers.

## Current State

### BioRxiv API Limitations
- **Current pygetpapers implementation**: Only supports date-based searches via bioRxiv API
- **API endpoint**: `https://api.biorxiv.org/details/{source}/{interval}/{cursor}`
- **Supported queries**: Date intervals only (e.g., "2021-01-01" to "2021-12-31")
- **No text search**: Cannot search by keywords, titles, authors, or content

### BioRxiv Website Capabilities
- **Web search interface**: `https://www.biorxiv.org/search/`
- **Text-based search**: Supports keyword queries like "urban heat island"
- **Rich filtering**: Subject area, article type, date range, etc.
- **Pagination**: Results displayed across multiple pages
- **Metadata extraction**: Titles, authors, DOIs, abstracts, publication dates

## Web Scraping Potential

### Advantages
1. **Text-based search**: Enable keyword searches that users expect
2. **Rich metadata**: Extract comprehensive paper information
3. **Filtering options**: Support subject areas, article types, date ranges
4. **User-friendly**: Matches user expectations from bioRxiv website
5. **Complementary**: Works alongside existing API for date-based searches

### Technical Feasibility
1. **Structured HTML**: bioRxiv search results have consistent structure
2. **RESTful URLs**: Search queries are URL-encoded and predictable
3. **Pagination support**: Can handle large result sets
4. **Rate limiting**: Can implement respectful scraping practices

### Implementation Approach

#### 1. Web Scraper Module
```python
class BioRxivWebScraper:
    def search_papers(self, query: str, max_results: int = 100) -> Dict[str, Any]:
        # Scrape bioRxiv search interface
        # Return structured results
        
    def get_paper_details(self, doi: str) -> Optional[Dict[str, Any]]:
        # Get detailed information for specific paper
        
    def save_results(self, results: Dict[str, Any], output_dir: str):
        # Save results in pygetpapers format
```

#### 2. Integration with pygetpapers
- **New repository type**: `biorxiv_web` for web-based searches
- **Fallback mechanism**: Use API for date searches, web scraper for text searches
- **Unified interface**: Same command-line interface, different backend
- **Result compatibility**: Same output format as existing repositories

#### 3. Streamlit UI Integration
- **Repository selection**: Add "bioRxiv (Web Search)" option
- **Query support**: Enable text queries for bioRxiv
- **Progress tracking**: Show scraping progress
- **Error handling**: Graceful fallback to API-only mode

## Technical Implementation

### Search URL Structure
```
https://www.biorxiv.org/search/urban%252Bheat%252Bisland
```

### HTML Structure Analysis
The search results page contains:
- **Paper entries**: Individual paper listings with metadata
- **Pagination**: Navigation controls for multiple pages
- **Filters**: Subject area, article type, date range selectors
- **Sorting**: Relevance, date, title options

### Data Extraction Points
1. **Title**: Paper title with link to full text
2. **Authors**: Author list with affiliations
3. **DOI**: Digital Object Identifier
4. **Publication date**: When paper was posted
5. **Subject area**: Research category
6. **Article type**: Research Article, Review, etc.
7. **Abstract**: Paper summary (if available)
8. **PDF link**: Direct link to full text

### Error Handling
1. **Network errors**: Retry with exponential backoff
2. **HTML parsing errors**: Graceful degradation
3. **Rate limiting**: Respect robots.txt and implement delays
4. **Missing data**: Handle incomplete results gracefully

## Ethical Considerations

### Responsible Scraping
1. **Rate limiting**: Implement delays between requests
2. **User agent**: Identify scraper in headers
3. **Robots.txt**: Respect website crawling policies
4. **Terms of service**: Review bioRxiv's terms for scraping

### Legal Compliance
1. **Copyright**: Respect paper copyrights
2. **Terms of use**: Follow bioRxiv's terms of service
3. **Attribution**: Properly credit bioRxiv as data source
4. **Usage limits**: Implement reasonable usage restrictions

## Integration Strategy

### Phase 1: Proof of Concept
1. **Basic scraper**: Implement core scraping functionality
2. **Data extraction**: Parse search results and paper details
3. **Output format**: Match pygetpapers JSON structure
4. **Testing**: Validate with sample queries

### Phase 2: pygetpapers Integration
1. **Repository class**: Create `BioRxivWeb` repository class
2. **Command-line interface**: Add `--api biorxiv_web` option
3. **Configuration**: Add to `config.ini`
4. **Documentation**: Update user guides

### Phase 3: Streamlit UI Enhancement
1. **Repository selection**: Add web search option
2. **Query interface**: Enable text queries for bioRxiv
3. **Progress tracking**: Show scraping progress
4. **Error handling**: Graceful fallback mechanisms

### Phase 4: Advanced Features
1. **Filtering**: Support subject areas and article types
2. **Pagination**: Handle large result sets
3. **Caching**: Implement result caching
4. **Export options**: CSV, HTML, XML output

## Alternative Approaches

### 1. Rxivist Integration
- **Current solution**: Use existing Rxivist API for text search
- **Limitations**: Metadata only, no full text
- **Advantage**: Already implemented and working

### 2. Hybrid Approach
- **Text queries**: Use web scraper
- **Date queries**: Use existing API
- **Best of both**: Combine strengths of each approach

### 3. API Enhancement
- **Contact bioRxiv**: Request text search API endpoints
- **Collaboration**: Work with bioRxiv on API improvements
- **Long-term**: Sustainable solution if bioRxiv provides API

## Implementation Challenges

### Technical Challenges
1. **HTML parsing**: bioRxiv may change page structure
2. **Rate limiting**: Need to implement respectful scraping
3. **Error handling**: Robust error recovery mechanisms
4. **Maintenance**: Keep up with website changes

### Legal/Policy Challenges
1. **Terms of service**: Ensure compliance with bioRxiv terms
2. **Rate limiting**: Implement appropriate usage limits
3. **Attribution**: Properly credit bioRxiv
4. **Usage monitoring**: Track and limit usage

### User Experience Challenges
1. **Performance**: Web scraping is slower than API calls
2. **Reliability**: Dependent on bioRxiv website availability
3. **Error messages**: Clear feedback when scraping fails
4. **Fallback options**: Graceful degradation to API-only mode

## Recommendations

### Immediate Actions
1. **Research bioRxiv terms**: Review terms of service for scraping
2. **Prototype scraper**: Build proof-of-concept implementation
3. **Test with sample queries**: Validate scraping functionality
4. **Document approach**: Create implementation plan

### Medium-term Actions
1. **Implement basic scraper**: Core functionality with error handling
2. **Integrate with pygetpapers**: Add as new repository type
3. **Update Streamlit UI**: Add web search option
4. **User testing**: Validate with real users

### Long-term Actions
1. **Monitor bioRxiv changes**: Keep scraper updated
2. **Explore API options**: Contact bioRxiv about API enhancements
3. **Community feedback**: Gather user input on approach
4. **Documentation**: Comprehensive user and developer guides

## Conclusion

Web scraping bioRxiv's search interface offers significant potential to enhance pygetpapers' functionality by providing text-based search capabilities. While there are technical and ethical considerations, a well-implemented scraper could:

1. **Improve user experience**: Enable expected text search functionality
2. **Complement existing features**: Work alongside API-based date searches
3. **Provide rich metadata**: Extract comprehensive paper information
4. **Maintain compatibility**: Use existing pygetpapers output formats

The key is implementing this responsibly with proper rate limiting, error handling, and respect for bioRxiv's terms of service. The proof-of-concept scraper demonstrates the technical feasibility, and the integration strategy provides a clear path forward.

## Next Steps

1. **Legal review**: Confirm scraping compliance with bioRxiv terms
2. **Technical validation**: Test scraper with real bioRxiv pages
3. **User feedback**: Gather input on desired features
4. **Implementation planning**: Develop detailed implementation roadmap 