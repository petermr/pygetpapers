# arXiv Repository Capabilities

## Overview
arXiv is a preprint repository for physics, mathematics, computer science, and related fields. **This repository is DISABLED in pygetpapers due to arXiv's policy against automated downloads.**

## Status: DISABLED

| Feature | Status | Details |
|---------|--------|---------|
| **API Access** | ❌ Disabled | Policy prohibits automated access |
| **Web Scraping** | ❌ Disabled | Policy prohibits scraping |
| **Metadata** | ❌ Disabled | No access to any content |
| **PDF Downloads** | ❌ Disabled | No access to any content |
| **XML/JATS** | ❌ Disabled | No access to any content |
| **HTML** | ❌ Disabled | No access to any content |
| **Figures** | ❌ Disabled | No access to any content |
| **Tables** | ❌ Disabled | No access to any content |
| **Supplementary Files** | ❌ Disabled | No access to any content |

## Policy Restrictions

### arXiv's Official Policy
- **Bulk Data Access**: arXiv provides official bulk data access through their S3 bucket
- **Automated Downloads**: Prohibited for individual papers
- **Web Scraping**: Explicitly forbidden
- **API Limitations**: No public API for automated downloads

### Official Guidance
According to arXiv's help documentation:
- Use their official bulk data access for large-scale downloads
- Respect rate limits and access policies
- Do not scrape their website
- Contact arXiv for special access requirements

## Why Disabled

### Technical Reasons
- **Policy Violation**: Automated downloads violate arXiv's terms of service
- **Legal Compliance**: Must respect repository policies
- **Sustainability**: Prevents service disruption
- **Best Practices**: Follows ethical scraping guidelines

### Alternative Approaches
- **Official Bulk Data**: Use arXiv's S3 bucket for bulk downloads
- **Manual Access**: Individual paper downloads through web interface
- **API Alternatives**: Use other repositories for similar content

## Implementation Notes

### Code Status
- **Implementation**: Exists but disabled
- **Error Message**: Raises `PygetpapersError` when accessed
- **Configuration**: Marked as disabled in core configuration

### Error Handling
```python
if self.query_namespace[API] == "arxiv":
    raise PygetpapersError(
        "arXiv support is DISABLED in pygetpapers due to arXiv's policy against scraping or automated downloads. See https://arxiv.org/help/bulk_data for official guidance."
    )
```

## Alternative Repositories

### For Similar Content
- **Physics**: Consider other physics repositories
- **Mathematics**: Use specialized math repositories
- **Computer Science**: Use CS-specific repositories
- **General Science**: Use Europe PMC, Crossref, or OpenAlex

### Recommended Alternatives
- **Europe PMC**: For biomedical and life sciences
- **BioRxiv**: For biology preprints
- **Crossref**: For comprehensive metadata
- **OpenAlex**: For open access indicators

## Maintenance Notes

**Last Updated**: January 2025

**Update Frequency**: Update when:
- arXiv policy changes
- Alternative repositories become available
- New access methods are approved
- Legal requirements change

**Information Sources**:
- arXiv help documentation
- arXiv bulk data access information
- Legal compliance requirements
- Community feedback

## Official Resources

### arXiv Documentation
- **Bulk Data Access**: https://arxiv.org/help/bulk_data
- **Terms of Service**: https://arxiv.org/help/terms_of_service
- **API Documentation**: https://arxiv.org/help/api
- **Contact Information**: https://arxiv.org/help/contact

### Recommended Actions
1. **For Bulk Downloads**: Use arXiv's official S3 bucket
2. **For Individual Papers**: Use web interface
3. **For Research**: Consider alternative repositories
4. **For Compliance**: Follow arXiv's official guidelines

---

*arXiv is disabled in pygetpapers to respect their policy against automated downloads. Users should use arXiv's official bulk data access or alternative repositories for their research needs.* 