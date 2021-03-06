# JOSS article

# Justification

Many users of the scientific literature want to download thousands of articles and analyse them by Mantural Language Processing (NLP) through Text and Data Miniing (TDM) or Content Mining.
The typical text-based searches on sites are broad, with many false positives and often only based on abstracts. We know of cases where systematic reviewers downloaded 30,000 articles and eventually used 30. 
Retrieval is often done by crawling / scraping sites, such as journals but is easier and faster when these articles are in Open Access repositories such as arXiv, Europe/PMC biorxiv, medrxiv.
But each repository has its own API and functionality, which makes it hard for individuals to (a) access (b) set flags (c) be generic

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

# implementation

* history `getpapers` => `pygetpapers`

# testing and examples


# limitations

* speed
* multithreading


