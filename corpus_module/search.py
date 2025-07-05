"""
Corpus search functionality.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from collections import defaultdict
import lxml.etree as ET
from lxml.html import HTMLParser

logger = logging.getLogger(__name__)

# Constants
HTML_WITH_IDS = "html_with_ids"


class CorpusSearch:
    """
    Search functionality for corpus analysis.
    """

    @classmethod
    def search_files_with_phrases_write_results(cls, infiles: List[Union[str, Path]], 
                                               phrases: Optional[List[str]] = None, 
                                               para_xpath: Optional[str] = None, 
                                               outfile: Optional[Union[str, Path]] = None, 
                                               debug: bool = False):
        """
        Iterate over files in corpus and search for phrases.
        
        Args:
            infiles: List of input files to search
            phrases: List of phrases to search for
            para_xpath: XPath for paragraph elements
            outfile: Output file for results
            debug: Enable debug logging
            
        Returns:
            HTML document with search results
        """
        if phrases is None:
            logger.error("no phrases")
            return None
            
        all_hits_dict = dict()
        url_list_by_phrase_dict = defaultdict(list)
        
        if not isinstance(phrases, list):
            phrases = [phrases]
            
        all_paras = []
        for infile in infiles:
            paras = cls.search_paras_with_id_and_create_dict(all_hits_dict, infile, para_xpath, phrases,
                                                     url_list_by_phrase_dict)
            all_paras.extend(paras)

        if debug:
            print(f"para count: {len(all_paras)}")
            
        html1 = cls.create_html_from_hit_dict(url_list_by_phrase_dict)
        assert html1 is not None
        
        if outfile:
            outfile = Path(outfile)
            outfile.parent.mkdir(exist_ok=True, parents=True)
            with open(outfile, "w", encoding="UTF-8") as f:
                if debug:
                    print(f" hitdict {url_list_by_phrase_dict}")
                cls.write_html_file(html1, outfile, debug=True)
                
        return html1

    @classmethod
    def search_paras_with_id_and_create_dict(cls, all_hits_dict: Dict, infile: Union[str, Path], 
                                            para_xpath: Optional[str], phrases: List[str],
                                            url_list_by_phrase_dict: Dict[str, List[str]]):
        """
        Read file, create HTML, find paras_with_id, and search for phrases.
        
        Args:
            all_hits_dict: Dictionary to accumulate hits
            infile: Input file path
            para_xpath: XPath for paragraph elements
            phrases: List of phrases to search for
            url_list_by_phrase_dict: Dictionary to accumulate URLs by phrase
            
        Returns:
            List of paragraph elements
        """
        infile_path = Path(infile)
        assert infile_path.exists(), f"{infile} does not exist"
        
        try:
            html_tree = lxml.etree.parse(str(infile), HTMLParser())
        except Exception as e:
            logger.error(f"Error parsing {infile}: {e}")
            return []
            
        paras = cls.find_paras_with_ids(html_tree, para_xpath=para_xpath)
        
        # This would need to be implemented based on the original functionality
        # For now, we'll create a placeholder
        para_id_by_phrase_dict = cls.create_search_results_para_phrase_dict(paras, phrases)
        
        if para_id_by_phrase_dict is not None and len(para_id_by_phrase_dict) > 0:
            cls.add_hit_with_filename_and_para_id(all_hits_dict, url_list_by_phrase_dict, infile,
                                                  para_id_by_phrase_dict)
        return paras

    @classmethod
    def add_hit_with_filename_and_para_id(cls, all_hits_dict: Dict, hit_dict: Dict, 
                                         infile: Union[str, Path], phrase_by_para_id_dict: Dict[str, List[str]]):
        """
        Add non-empty hits in hit_dict to all_dict.
        
        Args:
            all_hits_dict: Accumulates para_phrase_dict by infile
            hit_dict: Accumulates URL by hit
            infile: Input file path
            phrase_by_para_id_dict: Dictionary mapping paragraph IDs to phrases
        """
        infile_s = cls.create_url_from_filename(infile)

        item_paras = [item for item in phrase_by_para_id_dict.items() if len(item[1]) > 0]
        if len(item_paras) > 0:
            all_hits_dict[infile] = phrase_by_para_id_dict
            for para_id, hits in phrase_by_para_id_dict.items():
                for hit in hits:
                    url = f"{infile_s}#{para_id}"
                    hit_dict[hit].append(url)

    @classmethod
    def create_url_from_filename(cls, infile: Union[str, Path]) -> str:
        """
        Create URL from filename.
        
        Args:
            infile: Input file path
            
        Returns:
            URL string
        """
        infile_s = str(infile)
        infile_s = infile_s.replace("\\", "/")
        infile_s = infile_s.replace("%5C", "/")
        return infile_s

    @classmethod
    def create_html_from_hit_dict(cls, hit_dict: Dict[str, List[str]]):
        """
        Create HTML from hit dictionary.
        
        Args:
            hit_dict: Dictionary mapping terms to URLs
            
        Returns:
            HTML document
        """
        html = cls.create_html_with_empty_head_body()
        body = cls.get_body(html)
        ul = ET.SubElement(body, "ul")
        
        for term, hits in hit_dict.items():
            li = ET.SubElement(ul, "li")
            p = ET.SubElement(li, "p")
            p.text = f"term: {term}"
            ul1 = ET.SubElement(li, "ul")
            
            for hit in hits:
                hit = str(hit).replace("%5C", "/")
                li1 = ET.SubElement(ul1, "li")
                a = ET.SubElement(li1, "a")
                a.text = hit.replace(f"/{HTML_WITH_IDS}.html", "")
                ss = "ipcc/"
                try:
                    idx = a.text.index(ss)
                except Exception as e:
                    print(f"cannot find substring {ss} in {a.text}")
                    continue
                a.text = a.text[idx + len(ss):]
                a.attrib["href"] = hit
                
        return html

    @classmethod
    def find_paras_with_ids(cls, html_tree, para_xpath: Optional[str] = None) -> List[Any]:
        """
        Find paragraphs with IDs in HTML tree.
        
        Args:
            html_tree: HTML document tree
            para_xpath: XPath for paragraph elements
            
        Returns:
            List of paragraph elements
        """
        # This would need to be implemented based on the original functionality
        # For now, return empty list
        return []

    @classmethod
    def create_search_results_para_phrase_dict(cls, paras: List[Any], phrases: List[str]) -> Dict[str, List[str]]:
        """
        Create search results dictionary mapping paragraph IDs to phrases.
        
        Args:
            paras: List of paragraph elements
            phrases: List of phrases to search for
            
        Returns:
            Dictionary mapping paragraph IDs to matching phrases
        """
        # This would need to be implemented based on the original functionality
        # For now, return empty dict
        return {}

    # Utility methods
    @staticmethod
    def create_html_with_empty_head_body():
        """Create basic HTML document structure."""
        html = ET.Element("html")
        head = ET.SubElement(html, "head")
        body = ET.SubElement(html, "body")
        return html

    @staticmethod
    def get_body(htmlx):
        """Get body element from HTML document."""
        return htmlx.xpath("body")[0]

    @staticmethod
    def write_html_file(htmlx, outfile: Union[str, Path], debug: bool = False):
        """
        Write HTML document to file.
        
        Args:
            htmlx: HTML document
            outfile: Output file path
            debug: Enable debug logging
        """
        if debug:
            logger.info(f"writing HTML to {outfile}")
            
        with open(outfile, "w", encoding="UTF-8") as f:
            text = ET.tostring(htmlx, encoding='unicode', pretty_print=True)
            f.write(text) 