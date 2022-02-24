---
title: '`pygetpapers`: a Python library for automated retrieval of scientific literature
tags:
  - Python
  - REST API
authors:
  - name: Ayush Garg
    orcid:  0000-0001-7016-747X
    affiliation: 1
  - name: Richard D Smith-Unna
    orcid:  0000-0001-8721-7197
    affiliation: 2
  - name: Peter Murray-Rust
    orcid:  0000-0003-3386-3972
    affiliation: 3

date: February 2022
bibliography: paper.bib
---
# JOSS article

# Justification

An increasing amount of research, particularly in medicine and applied science, is now based on meta-analysis and systematic review of the existing literature [@systematic_review]. In such reviews, scientists frequently download thousands of articles and analyze them by Natural Language Processing (NLP) through Text and Data Mining (TDM) or Content Mining. A common approach is to search bibliographic resources with keywords, download the hits, scan them manually, and reject papers that do not fit the criteria for the meta-analysis.
The typical text-based searches on sites are broad, with many false positives and often only based on abstracts. We know of cases where systematic reviewers downloaded 30,000 articles and eventually used 30.
Retrieval is often done by crawling/scraping sites, such as journals but is easier and faster when these articles are in Open Access repositories such as arXiv, Europe/PMC biorxiv, medrxiv.
But each repository has its own API and functionality, which makes it hard for individuals to (a) access (b) set flags (c) use generic queries.

In 2015 we reviewed tools for scraping websites and decided that none met our needs and so developed `getpapers` [@getpapers], with the key advance of integrating a query submission with bulk fulltext-download of all the hits. `getpapers` was written in NodeJs and has now been completely rewritten in Python3 (`pygetpapers`) for easier distribution and integration. Typical use of `getpapers` is shown in a recent paper [@getpapers_use] where the authors "analyzed key term frequency within 20,000 representatives [Antimicrobial Resistance] articles".

An important aspect is to provide a simple cross-platform approach for scientists who may find tools like `curl` too complex and want a one-line command to combine the search, download, and analysis into a single: "please give me the results". We've tested this on many interns who learn `pygetpapers` in minutes. It was also easy to wrap it `tkinter GUI`[@tkinter]. The architecture of the results is simple and natural, based on full-text files in the normal filesystem. The result of `pygetpapers` is interfaced using a “master” json file (for eg. eupmc_results.json), which allows corpus to be reused/added to. This allows maximum flexibility of re-use and some projects have large amounts of derived data in these directories.

```
pygetpapers -q "METHOD: invasive plant species" -k 10 -o "invasive_plant_species_test" -c --makehtml -x --save_query
```

OUTPUT:
```  
INFO: Final query is METHOD: invasive plant species
INFO: Total Hits are 17910
0it [00:00, ?it/s]WARNING: Keywords not found for paper 1
WARNING: Keywords not found for paper 4
1it [00:00, 164.87it/s]
INFO: Saving XML files to C:\Users\shweata\invasive_plant_species_test\*\fulltext.xml
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:21<00:00,  2.11s/it]
```

  <h2 align="center">Fig.1 Example query of `pygetpapers`</h2>

The number and type of scientific repositories (especially preprints) is expanding , and users do not want to use a different tool for each new one. `pygetpapers` is built on a modular system and repository-specific code can be swapped in as needed. Often they use different query systems and `pygetpapers` makes a start on simplifying this. By configuring repositories in a configuration file, users can easily configure support for new repositories. 
    
```
[europe_pmc]
query_url=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
citationurl=https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid}/citations?page=1&pageSize=1000&format=xml
referencesurl=https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid}/references?page=1&pageSize=1000&format=xml
xmlurl=https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML
suppurl=https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles
zipurl= http://europepmc.org/ftp/suppl/OA/{key}/{pmcid}.zip
date_query=SUPPORTED
term=SUPPORTED
update=SUPPORTED
restart=SUPPORTED
class_name=EuropePmc
library_name= europe_pmc
features_not_supported = ["filter",]
```
  
<h2 align="center">Fig.2 Example configuration for a repository (europePMC)</h2>

Many **searches** are simple keywords or phrases. However, these often fail to include synonyms and phrases and authors spend time creating complex error-prone boolean queries. We have developed a dictionary-based approach to automate much of the creation of complex queries.

The **downloaded material** is inherently complex. See [Data]
Some of this has been systematized, especially in biosciences, and the NIH (US National Institutes of Health) led to the JATS/NISO standard to create highly structured documents.

Frequently users want to search **incrementally**, e.g. downloading part and resuming later (especially with poor connectivity where work is often lost). Also, `pygetpapers` allows regular updates, e.g. weekly searches of preprint servers.

`pygetpapers` takes the approach of downloading once and re-analyzing later on local filestore. This saves repeated querying where connections are poor or where there is suspicion that publishers may surveil users. Moreover, publishers rarely provide more than full-text Boolean searches, whereas local tools can analyze sections and non-textual material.

We do not know of other tools which have the same functionality. `curl` [@curl] requires detailed knowledge of the download protocol. VosViewer [@VOSviewer] is mainly aimed at bibliography/citations.

# Overview of the architecture

## Data

The download may be repository-dependent but usually contains:
* download metadata. (query, date, errors, etc.)
* journal/article metadata. We use JATS-NISO [@JATS] which is widely used by publishers and repository owners, especially in bioscience and medicine. There are over 200 tags. 
* fulltext. This can be 
   - XML (fulltext and metadata) 
   - images (these may not always be available)
   - tables (these are often separate)
   - PDF - usually includes the whole material but not machine-sectioned
   - HTML . often avaliable on websites
* supplemental data. This is very variable, often as PDF but also raw data files and sometimes zipped. It is not systematically arranged but `pygetpapers` allows for some heuristics.

![Fig.3 Architecture of `pygetpapers`](../resources/archietecture.png)

<h2 align="center">Fig.3 Architecture of `pygetpapers`</h2>

This directory structure is designed so that analysis tools can add computed data for articles


```
C:.
│   eupmc_results.json
│
├───PMC8157994
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8180188
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8198815
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8216501
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8309040
│       eupmc_result.json
│       fulltext.xml
│
└───PMC8325914
        eupmc_result.json
        fulltext.xml
```
<h2 align="center">Fig.4 Typical download directory</h2>


## Code 

### Download protocol

Most repository APIs provide a cursor-based approach to querying:
1. A query is sent and the repository creates a list of M hits (pointers to documents), sets a cursor start, and returns this information to the `pygetpapers` client.
2. The client requests a chunk of size N <= M (normally 25-1000) and the repository replies with N pointers to documents.
3. The server response is pages of hits (metadata) as XML , normally <= 1000 hits per page , (1 sec) 
4. `pygetpapers` - incremental aggregates XML metadata as python dict in memory - small example for paper
5. If cursor indicates next page, submits a query for next page, else if end terminates this part
6. When finished all pages, writes metadata to CProject (Top level project directory) as JSON (total, and creates CTrees (per-article directories) with individual metadata)
7. Recover from crashes, restart (if needed) 

The control module `pygetpapers` reads the commandline and
* Selects the repository-specific downloader
* Creates a query from user input and/or terms from dictionaries
* Adds options and constraints
* Downloads according to the protocol above, including recording progress in a metadata file

# Generic downloading concerns

* Download speeds. Excessively rapid or voluminous downloads can overload servers and are sometimes hostile (DOS). We have discussed this with major sites (EPMC, biorXiv, Crossref etc. and have a default (resettable) delay in `pygetpapers`. 
* Authentication (alerting repo to downloader header). `pygetpapers` supports anonymous, non-authenticated, access but includes a header (e.g. for Crossref)

# Design
* commandline (can be later wrapped in GUIs).
* modular (one module per repo)
* abstraction (e.g. of DATE functions)
* supports both metadata and content
* responsive to repository responses

# Implementation

`getpapers` was implemented in `NodeJS` which allows multithreading and therefore potentially download rates of several XML documents per second on a fast line. Installing `NodeJS` was a problem on some systems (especially Windows) and was not well suited for integration with scientific libraries (mainly coded in Java and Python). We, therefore, decided to rewrite in Python, keeping only the command line and output structure, and have found very easy integration with other tools, including GUIs. `pygetpapers` can be run both as a command-line tool and a module, which makes it versatile. 

# Interface with other tools

Downloading is naturally modular, rather slow, and we interface by writing all output to the filesystem. This means that a wide range of tools (Unix, Windows, Java, Python, etc.) can analyze and transform it. The target documents are usually static so downloads only need to be done once.
Among our own downstream tools are
* `pyami` [@pyami] - sectioning the document
* `docanalysis` [@docanalysis] - textual analysis and Natural Language Processing
* `pyamiimage` [@pyamiimage] - analysis of the content of images in downloaded documents
* third party text analysis of PDF using GROBID[@GROBID] and PDFBox[@PDFBox].

# Acknowledgements

We thank Dr. Peter Murray-Rust for the support and help with the design of the manuscript. 




