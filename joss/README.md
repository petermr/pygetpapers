# JOSS article

# Justification

An increasing amount of research, particularly in medicine and applied science,  is now based on meta-analysis and sytematic review of the existing literature (examples. https://systematicreviewsjournal.biomedcentral.com/). In such reviews scientists frequently download thousands of articles and analyse them by Natural Language Processing (NLP) through Text and Data Mining (TDM) or Content Mining (ref). A common approach is to search bibliographic resources with keywords, download the hits, scan then manually and reject papers that do not fit the criteria for the meta-analysis.
The typical text-based searches on sites are broad, with many false positives and often only based on abstracts. We know of cases where systematic reviewers downloaded 30,000 articles and eventually used 30. 
Retrieval is often done by crawling / scraping sites, such as journals but is easier and faster when these articles are in Open Access repositories such as arXiv, Europe/PMC biorxiv, medrxiv.
But each repository has its own API and functionality, which makes it hard for individuals to (a) access (b) set flags (c) use generic queries.

In 2015 we reviewed tools for scraping websites and decided that none met our needs and so developed `getpapers`, with the key advance of integrating a query submission with bulk fulltext-download of all the hits. `getpapers` was written in NodeJs and has now been completely rewritten in Python3 (`pygetpapers`) for easier distribution and integration. Typical use of `getpapers` is shown in a recent paper (https://europepmc.org/article/MED/33916878) where the authors "analyzed key term frequency within 20,000 representative [Antimcrobial Resistance] articles".


# overview of architecture

# Existing tools

* curl
* VOSViewer
* scrapy

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


