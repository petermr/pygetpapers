"""
Corpus query management functionality.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any
import lxml.etree as ET

logger = logging.getLogger(__name__)

# Constants
HTML_WITH_IDS = "html_with_ids"
TABLE_HITS_SUFFIX = "table_hits.html"


class CorpusQuery:
    """
    Holds query and related info (hits, files).
    """

    def __init__(self, query_id: Optional[str] = None, phrasefile: Optional[Union[str, Path]] = None,
                 phrases: Optional[List[str]] = None, outfile: Optional[Union[str, Path]] = None):
        """
        Initialize corpus query.
        
        Args:
            query_id: Unique ID of query
            phrasefile: File containing phrases
            phrases: List of phrases to search for
            outfile: Output file for results
        """
        self.query_id = query_id
        self.phrasefile = Path(phrasefile) if phrasefile else None
        self.phrases = phrases
        if self.phrasefile and not self.phrases:
            self.phrases = self._read_strings_from_path(self.phrasefile)

        self.outfile = Path(outfile) if outfile else None
        self.corpus = None
        logger.debug(f"made query {self}")

    def __str__(self):
        """String representation of query."""
        s = f"""CorpusQuery
query_id:  {self.query_id}
phrasefile:{self.phrasefile}
phrases:   {None if not self.phrases else len(self.phrases)}
outfile:   {self.outfile}
corpus:    {None if self.corpus is None else self.corpus.__hash__()}
"""
        return s

    def run_query_make_table_TUTORIAL(self, query: Union[str, List[str]], query_id: str, 
                                     indir: Union[str, Path], outdir: Union[str, Path], 
                                     outfile: Optional[Union[str, Path]] = None):
        """
        Take query string and query_id, create input and output filenames,
        run query, create table of results.
        
        Args:
            query: Query string or list of query strings
            query_id: String without spaces to uniquely identify the query
            indir: Top directory of corpus
            outdir: Output top directory
            outfile: Output HTML file with tables
            
        Returns:
            tuple: (html_document, query_id)
        """
        self.debug = True
        if not query:
            raise ValueError("No query given")
        if isinstance(query, str):
            self.phrases = [query]
        if not query_id:
            raise ValueError("No query_id given")
        query_id = query_id.strip()
        if " " in query_id:
            raise ValueError(f"no spaces allowed in query_id, found {query_id}")
        self.query_id = query_id

        if indir is None or not Path(indir).exists():
            logger.error(f"input directory must exist {indir}")
        self.indir = Path(indir)
        self.outfile = Path(outfile) if outfile else None
        if not self.outfile:
            self.outfile = self.indir / f"{query_id}.html"

        self.para_xpath = None
        self.globstr = f"{str(self.indir)}/**/{HTML_WITH_IDS}.html"
        self.infiles = self._posix_glob(self.globstr, recursive=True)
        
        # For tutorial, use a simple phrase
        self.phrases = ["methane emissions"]
        self.colheads = ["term", "ref", "para"]

        # This would need to be implemented based on the search functionality
        # For now, we'll create a placeholder
        logger.info(f"Running query: {query_id} with phrases: {self.phrases}")
        
        # Create a simple HTML table as placeholder
        from datatables_module import Datatables
        htmlx, table_body = Datatables.create_table(colheads=self.colheads, table_id=f"{query_id}_table")
        
        # Add some placeholder data
        tr = table_body.makeelement("tr")
        for col in self.colheads:
            td = tr.makeelement("td")
            td.text = f"placeholder_{col}"
            tr.append(td)
        table_body.append(tr)
        
        table_file = Path(outdir) / f"{self.query_id}_{TABLE_HITS_SUFFIX}"
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write(ET.tostring(htmlx, encoding='unicode', pretty_print=True))
            
        return htmlx, self.query_id

    @classmethod
    def extract_hits_by_url_from_nested_lists(cls, html_markup) -> Dict[str, List[str]]:
        """
        Extract hits by URL from nested lists in HTML markup.
        
        Args:
            html_markup: HTML document with search results
            
        Returns:
            Dictionary mapping URLs to hit terms
        """
        # This would need to be implemented based on the original functionality
        # For now, return empty dict
        return {}

    @classmethod
    def get_hits_as_term_ref_p_tuple_list(cls, term_id_by_url: Dict[str, List[str]]) -> List[Tuple[str, str, Any]]:
        """
        Get hits as list of (term, ref, para) tuples.
        
        Args:
            term_id_by_url: Dictionary mapping URLs to hit terms
            
        Returns:
            List of (term, ref, para) tuples
        """
        if term_id_by_url is None:
            logger.error(f"term_id_by_url is None")
            return None
            
        trp_list = []
        for ref in term_id_by_url.keys():
            bits = ref.split("#")
            file = bits[0]
            idref = bits[1] if len(bits) > 1 else ""
            term_p = term_id_by_url.get(ref)
            if term_p and len(term_p) >= 2:
                term = term_p[0]
                p = term_p[1]
                tuple_item = (term, ref, p)
                trp_list.append(tuple_item)

        return trp_list

    @classmethod
    def _add_hits_to_table(cls, tbody, term_ref_p_tuple_list: List[Tuple[str, str, Any]]):
        """
        Add hits to table body.
        
        Args:
            tbody: Table body element
            term_ref_p_tuple_list: List of (term, ref, para) tuples
        """
        if term_ref_p_tuple_list is None:
            logger.error(f"term_ref_p_tuple_list is None")
            return
            
        for term, ref, p in term_ref_p_tuple_list:
            if not isinstance(term, str):
                logger.warning(f"term is not string: {type(term)}")
                continue
            if not isinstance(ref, str):
                logger.warning(f"ref is not string: {type(ref)}")
                continue
                
            tr = tbody.makeelement("tr")
            tds = []
            for item in [term, ref, p]:
                tds.append(tr.makeelement("td"))
                
            tds[0].text = term
            
            # Create link for reference
            a = tds[1].makeelement("a")
            a.attrib["href"] = ref
            a.text = ref
            tds[1].append(a)

            # Add paragraph content
            if hasattr(p, 'itertext'):
                tds[2].text = ''.join(p.itertext())
            else:
                tds[2].text = str(p)
                
            for td in tds:
                tr.append(td)
            tbody.append(tr)

    @classmethod
    def make_hits_by_url(cls, search_html) -> Dict[str, List[str]]:
        """
        Make hits by URL from search HTML.
        
        Args:
            search_html: HTML document with search results
            
        Returns:
            Dictionary mapping URLs to hit terms
        """
        # This would need to be implemented based on the original functionality
        # For now, return empty dict
        return {}

    # Utility methods
    def _read_strings_from_path(self, path: Path) -> List[str]:
        """Read strings from file path."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return []

    def _posix_glob(self, pattern: str, recursive: bool = False) -> List[Path]:
        """Glob files using POSIX-style patterns."""
        return list(Path(".").glob(pattern)) 