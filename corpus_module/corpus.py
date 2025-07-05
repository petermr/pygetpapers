"""
Core corpus management functionality.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

# Constants
DATATABLES_HTML = "datatables.html"
SAVED_CONFIG_INI = "saved_config.ini"
HTML_WITH_IDS = "html_with_ids"
EUPMC_RESULTS_JSON = "eupmc_result.json"
TABLE_HITS_SUFFIX = "table_hits.html"


class AmiCorpus:
    """
    Main corpus management class supporting hierarchical directory structures.
    """

    def __init__(self,
                 topdir: Optional[Union[str, Path]] = None,
                 infiles: Optional[List[Union[str, Path]]] = None,
                 globstr: Optional[str] = None,
                 outfile: Optional[Union[str, Path]] = None,
                 make_descendants: bool = False,
                 mkdir: bool = False,
                 **kwargs):
        """
        Create new corpus with optional input data.
        
        Args:
            topdir: Input directory with files/subdirs as possible corpus components
            infiles: List of files to use (alternative to globstr)
            globstr: Create infiles using globbing under topdir (requires topdir)
            outfile: Output file path
            mkdir: Make topdir if doesn't exist (default=False)
            make_descendants: Makes AmiCorpusContainers for directories on tree
            **kwargs: Dict of per-corpus user-specified properties
        """
        self.topdir = Path(topdir) if topdir else None
        if self.topdir and not self.topdir.is_dir():
            raise ValueError(f"AmiCorpus() requires valid directory {self.topdir}")

        self.container_by_file = dict()
        # rootnode
        self.ami_container = self.create_corpus_container(
            self.topdir, make_descendants=make_descendants, mkdir=mkdir)
        self.infiles = infiles
        self.outfile = Path(outfile) if outfile else None
        self.globstr = globstr
        self.corpus_queries = dict()
        self.search_html = None
        self.eupmc_results = None
        self._make_infiles()
        self._make_outfile()

        self.make_special(kwargs)

    def __str__(self):
        """String representation of corpus."""
        values = []
        for key in self.corpus_queries.keys():
            value = self.corpus_queries.get(key)
            values.append(value)

        s = f"""AmiCorpus:
topdir:  {self.topdir}
globstr: {self.globstr}
infiles: {len(self.infiles) if self.infiles else 0}
outfile: {self.outfile}
"""
        s += "QUERIES"
        for (key, value) in self.corpus_queries.items():
            s += f"""
            {key}:
            {value.__str__()}
            """
        return s

    def _make_infiles(self):
        """Create infiles list from globstr if not provided."""
        if self.infiles:
            logger.info(f"taking infiles from list")
        else:
            if self.topdir and self.globstr:
                self.infiles = self._posix_glob(f"{self.topdir}/{self.globstr}", recursive=True)
        if self.infiles is None:
            logger.error(f"self.infiles is None")
            return
        logger.info(f"inputting {len(self.infiles)} files")
        return self.infiles

    def create_corpus_container(self, file: Optional[Union[str, Path]], 
                               bib_type: str = "None", make_descendants: bool = False, 
                               mkdir: bool = False):
        """
        Create container as child of self.
        
        Args:
            file: File or dir contained by container
            bib_type: Type of container
            make_descendants: Whether to create descendant containers
            mkdir: Whether to create directory if it doesn't exist
            
        Returns:
            AmiCorpusContainer instance
        """
        if file is None:
            logger.error("Container has no file")
            return None

        container = AmiCorpusContainer(self, file)
        container.bib_type = bib_type
        if not Path(file).exists() and mkdir:
            Path(file).mkdir(parents=True, exist_ok=True)
        if make_descendants:
            self.make_descendants(file)
        return container

    @property
    def root_dir(self):
        """Get root directory of corpus."""
        return self.ami_container.file if self.ami_container else None

    def make_descendants(self, file: Optional[Union[str, Path]] = None):
        """
        Creates AmiCorpusContainers for directory tree.
        
        Args:
            file: Directory to process (defaults to root_dir)
        """
        if file is None:
            file = self.root_dir
        if file is None or not Path(file).is_dir():
            logger.error(f"Cannot make file children for {file}")
            return
        files = self._get_children(file)
        for f in files:
            container = AmiCorpusContainer(self, f)
            container.make_descendants()

    def make_special(self, kwargs: Dict[str, Any]):
        """Manage repository specific functionality."""
        if "eupmc" in kwargs:
            self.eupmc_results = kwargs["eupmc"]

    @classmethod
    def make_datatables(cls, indir: Union[str, Path], outdir: Optional[Union[str, Path]] = None, 
                       outfile_h: Optional[Union[str, Path]] = None):
        """
        Create a JQuery DataTables HTML file from an AmiCorpus.
        
        Args:
            indir: Directory with corpus (normally created by pygetpapers)
            outdir: Output directory for datatables (if omitted uses indir)
            outfile_h: The HTML file created (may be changed)
        """
        if indir is None:
            logger.warning("No indir")
            return
        if outdir is None:
            outdir = indir
        if outfile_h is None:
            outfile_h = Path(outdir) / DATATABLES_HTML
            
        config_ini = Path(indir) / SAVED_CONFIG_INI
        Path(outdir).mkdir(parents=True, exist_ok=True)
        datatables = True
        epmc_infile = Path(indir) / EUPMC_RESULTS_JSON
        
        if epmc_infile.exists():
            cls.read_json_create_write_html_table(
                epmc_infile, outfile_h, wanted_keys=None, datatables=datatables,
                table_id=None, config_ini=config_ini)
            return
            
        # Try alternative filename
        infile = Path(indir) / EUPMC_RESULTS_JSON
        if infile.exists():
            cls.read_json_create_write_html_table(
                infile, outfile_h, wanted_keys=None, datatables=datatables, 
                table_id=None, config_ini=config_ini)
            return

    @classmethod
    def read_json_create_write_html_table(cls, infile: Union[str, Path], outfile_h: Union[str, Path],
                                         wanted_keys: Optional[List[str]] = None, datatables: bool = True,
                                         table_id: Optional[str] = None, config_ini: Optional[Union[str, Path]] = None):
        """
        Read JSON data and create HTML table.
        
        Args:
            infile: Input JSON file
            outfile_h: Output HTML file
            wanted_keys: Keys to include in table
            datatables: Whether to enable DataTables
            table_id: Table ID
            config_ini: Config file path
        """
        # This would need to be implemented based on the original functionality
        # For now, we'll create a basic implementation
        logger.info(f"Creating HTML table from {infile} to {outfile_h}")
        
        # Read JSON data
        with open(infile, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Create simple HTML table
        if datatables:
            from datatables_module import Datatables
            htmlx, tbody = Datatables.create_table(
                labels=list(data[0].keys()) if data else [], 
                table_id=table_id or "corpus_table"
            )
            
            # Add data rows
            for row in data:
                tr = tbody.makeelement("tr")
                for value in row.values():
                    td = tr.makeelement("td")
                    td.text = str(value)
                    tr.append(td)
                tbody.append(tr)
                
            # Write to file
            with open(outfile_h, 'w', encoding='utf-8') as f:
                f.write(ET.tostring(htmlx, encoding='unicode', pretty_print=True))

    def list_files(self, globstr: str) -> List[Path]:
        """
        Find files in corpus starting at root_dir.
        
        Args:
            globstr: Glob pattern to match files
            
        Returns:
            List of matching file paths
        """
        if globstr and self.root_dir:
            return self._posix_glob(str(self.root_dir / globstr), recursive=True)
        return []

    def create_datatables_html_with_filenames(self, html_glob: str, labels: List[str], 
                                            table_id: str, outpath: Optional[Union[str, Path]] = None, 
                                            debug: bool = True):
        """
        Create DataTables HTML with filenames.
        
        Args:
            html_glob: Glob string to find HTML files
            labels: Column labels
            table_id: Table ID
            outpath: Output path
            debug: Enable debug logging
            
        Returns:
            HTML document
        """
        html_files = sorted(self.list_files(globstr=html_glob))
        
        from datatables_module import Datatables
        self.datables_html, tbody = Datatables._create_html_for_datatables(labels, table_id)

        for html_file in html_files:
            if outpath:
                offset = self._get_relative_path(html_file, Path(outpath).parent, walk_up=True)
            else:
                offset = html_file.name
                
            tr = tbody.makeelement("tr")
            td = tr.makeelement("td")
            a = td.makeelement("a")
            a.attrib["href"] = str(offset)
            a.text = str(offset)
            td.append(a)
            tr.append(td)
            tbody.append(tr)

        if outpath:
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(ET.tostring(self.datables_html, encoding='unicode', pretty_print=True))

        return self.datables_html

    def make_infiles(self, maxfiles: int = 999999999) -> List[Path]:
        """
        Create infiles list from globstr.
        
        Args:
            maxfiles: Maximum number of files to include
            
        Returns:
            List of file paths
        """
        if self.globstr:
            self.infiles = self._posix_glob(self.globstr, recursive=True)[:maxfiles]
        return self.infiles

    def _make_outfile(self):
        """Create output file path if not provided."""
        if not self.outfile:
            pass  # Implementation depends on specific requirements

    def get_or_create_corpus_query(self, query_id: str, phrasefile: Optional[Union[str, Path]] = None,
                                  phrases: Optional[List[str]] = None, outfile: Optional[Union[str, Path]] = None):
        """
        Retrieve query by query_id. If not found, create new one.
        
        Args:
            query_id: Unique ID of query
            phrasefile: File containing phrases
            phrases: List of phrases
            outfile: Output file for results
            
        Returns:
            CorpusQuery instance
        """
        corpus_query = self.corpus_queries.get(query_id)
        if not corpus_query:
            corpus_query = CorpusQuery(
                query_id=query_id,
                phrasefile=phrasefile,
                phrases=phrases,
                outfile=outfile)
            self.corpus_queries[query_id] = corpus_query
            corpus_query.corpus = self

        return corpus_query

    def search_files_with_queries(self, query_ids: Union[str, List[str]], debug: bool = True) -> Dict[str, Any]:
        """
        Run queries. Assumes queries have been loaded and are recallable by ID.
        
        Args:
            query_ids: Single or list of query IDs
            debug: Enable debug logging
            
        Returns:
            Dictionary mapping query IDs to HTML results
        """
        html_by_query_id = dict()
        if isinstance(query_ids, str):
            query_ids = [query_ids]
        elif not isinstance(query_ids, list):
            raise ValueError(f"queries requires id/s as list or str, found {type(query_ids)}")
            
        for query_id in query_ids:
            query = self.corpus_queries.get(query_id)
            if query is None:
                logger.error(f"cannot find query: {query_id}")
                continue
            logger.debug(f"outfile==> {query.outfile}")
            
            # This would need to be implemented based on the search functionality
            # For now, we'll create a placeholder
            logger.info(f"Running query: {query_id}")
            
        return html_by_query_id

    # Utility methods
    def _posix_glob(self, pattern: str, recursive: bool = False) -> List[Path]:
        """Glob files using POSIX-style patterns."""
        return list(Path(".").glob(pattern))

    def _get_children(self, directory: Union[str, Path]) -> List[Path]:
        """Get child files/directories of a directory."""
        return list(Path(directory).iterdir())

    def _get_relative_path(self, file_path: Path, base_path: Path, walk_up: bool = False) -> str:
        """Get relative path from base path."""
        try:
            return str(file_path.relative_to(base_path))
        except ValueError:
            return str(file_path)


class AmiCorpusContainer:
    """
    Container for corpus components (files or directories).
    """

    def __init__(self, ami_corpus: AmiCorpus, file: Union[str, Path], 
                 bib_type: str = "unknown", mkdir: bool = False, exist_ok: bool = True):
        """
        Create corpus container for directory-structured corpus.
        
        Args:
            ami_corpus: Corpus to which this belongs
            file: File/directory on filesystem
            bib_type: Type of container (e.g., report)
            mkdir: Whether to create directory
            exist_ok: Whether to allow existing directory
        """
        if not isinstance(ami_corpus, AmiCorpus):
            raise ValueError(f"ami_corpus has wrong type {type(ami_corpus)}")
            
        self.ami_corpus = ami_corpus
        self.file = Path(file)
        self.ami_corpus.container_by_file[self.file] = self
        
        if not file:
            logger.error(f"No file argument")
            return None
            
        self.bib_type = bib_type
        self.child_container_list = []
        self.child_document_list = []

    @property
    def child_containers(self) -> List['AmiCorpusContainer']:
        """Get child containers."""
        child_containers = []
        if self.ami_corpus and self.file and self.file.is_dir():
            child_nodes = self.ami_corpus._get_children(self.file)
            for child_node in child_nodes:
                child_container = AmiCorpusContainer(self.ami_corpus, child_node)
                child_container.bib_type = "" if child_node.is_dir() else "file"
                child_containers.append(child_container)
        return child_containers

    def create_corpus_container(self, filename: str, bib_type: str = "unknown", 
                               make_descendants: bool = False, mkdir: bool = False):
        """
        Create a child container and optionally its actual directory.
        
        Args:
            filename: Name of the container
            bib_type: Type of container
            make_descendants: Whether to create descendants
            mkdir: Whether to create directory
            
        Returns:
            AmiCorpusContainer instance
        """
        if not filename:
            logger.error("filename is None")
            return None
            
        path = self.file / filename
        if mkdir and not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        else:
            if not path.is_dir():
                logger.error(f"{path} exists but is not a directory")
                return None
                
        corpus_container = AmiCorpusContainer(self.ami_corpus, path, bib_type=bib_type, mkdir=mkdir)
        self.child_container_list.append(corpus_container)
        return corpus_container

    def create_document(self, filename: str, text: Optional[str] = None, type: str = "unknown") -> Path:
        """
        Create document file with name and self as parent.
        
        Args:
            filename: Name of the document
            text: Content of the document
            type: Type of document
            
        Returns:
            Path to created document
        """
        document_file = self.file / filename
        document_file.touch()
        if text:
            with open(document_file, "w", encoding="UTF-8") as f:
                f.write(text)

        self.child_document_list.append(document_file)
        return document_file

    def make_descendants(self):
        """Create descendant containers if this is a directory."""
        if self.file and self.file.is_dir():
            self.ami_corpus.make_descendants(self.file) 