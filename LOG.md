# Pygetpapers Streamlit UI Development Log

## Team Feedback - [Date]

### Issues to Address:

1. **Documentation Issues:**
   - ❌ Remove `# noqa` comments from instructions - team doesn't understand them
   - ❌ Need clear migration guide from CLI to Streamlit

2. **UI/UX Improvements:**
   - ❌ Highlight the query box for better visibility
   - ❌ Reduce default paper downloading from current limit to 10
   - ❌ Create version without external dependencies (no plotly requirement)

3. **Functionality Issues:**
   - ❌ Plot doesn't show numbers of papers and years
   - ❌ Datatables show journal name as "Unknown" 
   - ❌ Figures facility needs significant work (deferred)
   - ❌ Clarify where corpus is created/stored

4. **Future Enhancements:**
   - ❌ Add filters based on metadata (journal name, authors)
   - ❌ Add filters based on fulltext content

## Implementation Status:

### Completed ✅
- Fixed Arxiv API bug (`Search.get()` → `list(Search.results())`)
- Fixed zip test to be realistic
- Fixed Streamlit blocking in CI
- Fixed CLI availability with `pip install -e .`
- Fixed Black formatting issues
- All 23 tests passing with 64% coverage
- CI/CD pipeline working
- ✅ Reduced default limit to 10 papers
- ✅ Highlighted query box with prominent styling
- ✅ Created migration guide (MIGRATION_GUIDE.md)
- ✅ Created no-dependencies version (streamlit_app_no_deps.py)

### In Progress 🔄
- Fixing journal name display issue
- Investigating plot functionality

### Pending ⏳
- Remove `# noqa` comments from instructions
- Fix plot to show numbers of papers and years
- Fix journal name display in datatables
- Document corpus location clearly
- Plan filter implementation
- Figures facility improvements (deferred)

## Technical Notes:
- Current default limit: ✅ Reduced to 10 papers
- Plotly dependency: ✅ Created no-deps version without plotly
- Corpus location: ✅ Files saved to `{repo_name}_{timestamp}` in current directory (e.g., `europe_pmc_20250121_143022`)
- Journal name issue: ✅ Fixed - was looking for `journalTitle` but should look for `journalInfo.journal.title`
- Query box: ✅ Highlighted with prominent styling and help text

## Next Steps:
1. Remove `# noqa` comments
2. Create migration guide
3. Highlight query box
4. Reduce default limit to 10
5. Create no-dependencies version
6. Fix plot functionality
7. Fix journal name display
8. Document corpus location
9. Plan filter implementation 