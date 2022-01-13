# JOSS article

# Justification

An increasing amount of research, particularly in medicine and applied science,  is now based on meta-analysis and sytematic review of the existing literature (examples. https://systematicreviewsjournal.biomedcentral.com/). In such reviews scientists frequently download thousands of articles and analyse them by Natural Language Processing (NLP) through Text and Data Mining (TDM) or Content Mining (ref). A common approach is to search bibliographic resources with keywords, download the hits, scan then manually and reject papers that do not fit the criteria for the meta-analysis.
The typical text-based searches on sites are broad, with many false positives and often only based on abstracts. We know of cases where systematic reviewers downloaded 30,000 articles and eventually used 30. 
Retrieval is often done by crawling / scraping sites, such as journals but is easier and faster when these articles are in Open Access repositories such as arXiv, Europe/PMC biorxiv, medrxiv.
But each repository has its own API and functionality, which makes it hard for individuals to (a) access (b) set flags (c) use generic queries.

In 2015 we reviewed tools for scraping websites and decided that none met our needs and so developed `getpapers`, with the key advance of integrating a query submission with bulk fulltext-download of all the hits. `getpapers` was written in NodeJs and has now been completely rewritten in Python3 (`pygetpapers`) for easier distribution and integration. Typical use of `getpapers` is shown in a recent paper (https://europepmc.org/article/MED/33916878) where the authors "analyzed key term frequency within 20,000 representative [Antimicrobial Resistance] articles".

An important aspect is to provide a simple cross-platform approach for scientists who may find tools like `curl` too complex and want a one-line command to combine the search, download and analysis into a single: "please give me the results". We've tested this on many interns who learn `pygetpapers` in minutes. It was also easy to wrap it tkinter` GUI (see below). The architecture of the results is also important and we base this on full-text files in the normal filesystem, allowing maximum flexibility of re-use.

The number and type of scientific repositories (espcially preprints) is expanding and users do not want to use a different tool for each new one. `pygetpapers` is built on a modular system and repository-specific code can be swapped in as needed. 

The content is inherently complex. A download consists of:
* the metadata for the operation (date, query, errors, etc.)
* the metadata for each article (authors, pubdate, journal, DOI, language, etc.)
* the fulltext content (abstract, introduction, methods, discussion, etc.)
* backmatter (references, permissions, ethics, etc.)
* non-text: tables, diagrams. images
* supplemental/supporting material
Much of this has been systematised and we use the JATS/NISO standard to create highly structured documents and their sections on filestore.

Frequently users want to search incrementally, e.g. downloading part and resuming later (especially with poor connectivity where work is often lost). Also `pygetpapers` allows regular updates , e.g. weekly searches of preprint servers.

`pygetpapers` takes the approach of downloading once and re-analysing later on local filestore. This saves repeated querying where connections are poor or where there is suspicion that publishers may surveill users (Brembs). Moreover publishers rarely provide more than full-text Boolean searches, whereas local tools can analyse sections, and non-textual material.

We do not know of othe tools which have the same functionality. `curl` requires detailed knowledge of the download protocol. VosViewer is 

# overview of architecture

## data

The download may be repository-dependent but usually contains:
* download metadata. (query, date, errors, etc.)
* journal/article metadata. We use JATS-NISO (ref) which is widely used by publishers and repository owners, especially in bioscience and medicine. There are over 200 tags. 
* fulltext. This can be 
   - XML (fulltext and metadata) 
   - images (these may not always be available)
   - tables (these are often separate
   - PDF - usually includes the whole material but not machine-sectioned
   - HTML . often avaliable on websites
* supplemental data. This is very variable, often as PDF but also raw data files and sometimes zipped. It is too varied for machines to analyse automatically.

see Fig 1 (typical download directory). This is designed so that analysis tools can add computed data for articles


## code 

### download protocol

Most repository APIs provide a cursor-based approach to querying:
1. a query is sent and the repository creates a list of M hits (pointers to documents), sets a cursor start and returns this information to the `pygetpapers` client.
2. The client requests a chunk of size N <= M (normally 25-1000) and the repository replies with N pointers to documents.
3. the client downloads the fulltext for each pointer (using REST) and continues until all N pointers are exhausted. 
4. the client resets the cursor mark for the next iteration. If there are no more pointers, break
5. goto 2


The control module `pygetpapers` reads the commandline and
* selects the repository-specific downloader
* creates a query from user input and/or terms from dictiomaries
* adds options and constraints
* downloads according to protocol above, including recording progress in a metadata file


# Existing tools


# problems

* Download speeds.
* Authentication (alerting repo to downloader header)
* Legal aspects.

# design
* commandline (can be later wrapped in GUIs)
* modular (one module per repo)
* abstraction (e.g. of DATE functions)
* supports both metadata and content
* responsive to repository responses

# mechanism of downloading
The download process for (most) servers of scientific articles is:
* create a RESTful query as URL 
* METADATA
* post query (includes optional cursor mark (units = pages), optional pagesize)
* server response is pages of hits (metadata) as XML , normally <= 1000 hits per page , (1 sec) 
* pygetpapers - incremental aggregates XML metadata as python dict in memory - small example for paper
* if cursor indicates next page, submits query for next page , else if end, terminates this part
* when finished all pages, writes metadata tp CProject as JSON (total, and creates CTrees with individual metadata)
* CONTENT
* from total metadata in memory, systematically download requested (optional content) (minutes, depending on size)
* recover from crashes, restart 

# implementation

* history `getpapers` => `pygetpapers`

# testing and examples


# limitations

* speed
* multithreading

# interface with other tools

* docanalysis
* 

