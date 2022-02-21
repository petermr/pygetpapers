# JOSS article

# Justification

An increasing amount of research, particularly in medicine and applied science, is now based on meta-analysis and systematic review of the existing literature [1]. In such reviews, scientists frequently download thousands of articles and analyze them by Natural Language Processing (NLP) through Text and Data Mining (TDM) or Content Mining. A common approach is to search bibliographic resources with keywords, download the hits, scan them manually, and reject papers that do not fit the criteria for the meta-analysis.
The typical text-based searches on sites are broad, with many false positives and often only based on abstracts. We know of cases where systematic reviewers downloaded 30,000 articles and eventually used 30.
Retrieval is often done by crawling/scraping sites, such as journals but is easier and faster when these articles are in Open Access repositories such as arXiv, Europe/PMC biorxiv, medrxiv.
But each repository has its own API and functionality, which makes it hard for individuals to (a) access (b) set flags (c) use generic queries.

In 2015 we reviewed tools for scraping websites and decided that none met our needs and so developed getpapers, with the key advance of integrating a query submission with bulk fulltext-download of all the hits. getpapers was written in NodeJs and has now been completely rewritten in Python3 (pygetpapers) for easier distribution and integration. Typical use of getpapers is shown in a recent paper [2] where the authors "analyzed key term frequency within 20,000 representatives [Antimicrobial Resistance] articles".

An important aspect is to provide a simple cross-platform approach for scientists who may find tools like curl too complex and want a one-line command to combine the search, download, and analysis into a single: "please give me the results". We've tested this on many interns who learn pygetpapers in minutes. It was also easy to wrap it tkinter GUI. The architecture of the results is simple and natural, based on full-text files in the normal filesystem. The result of pygetpapers is interfaced using a “master” json file (for eg. eupmc_results.json), which allows corpus to be reused/added to. This allows maximum flexibility of re-use and some projects have large amounts of derived data in these directories.

<p align="center">
  <img src="https://user-images.githubusercontent.com/62711517/153720690-771163fe-110b-4112-8d5a-36b28d94ebda.png" alt="pygetpapers" height="50%" width="50%">
  <h2 align="center">Fig.1 Example query of pygetpapers</h2>
</p>

The number and type of scientific repositories (especially preprints) is expanding and users do not want to use a different tool for each new one. pygetpapers is built on a modular system and repository-specific code can be swapped in as needed. Often they use different query systems and pygetpapers makes a start on simplifying this. By configuring repositories in a configuration file, users can easily configure support for new repositories. 

<p align="center">
  <img src="https://user-images.githubusercontent.com/62711517/153720720-927c3c58-96e5-4d38-865b-85f76d901e3b.png" alt="pygetpapers" height="50%" width="50%">
  <h2 align="center">Fig.2 Example configuration for a repository (europePMC)</h2>
</p>

Simple keyword searches often fail to include synonyms and phrases and authors spend time creating complex error-prone boolean queries. We have developed a dictionary-based approach to automate much of the creation of complex queries.

**The downloaded material is inherently complex.** A download consists of:
* the metadata for the operation (date, query, errors, etc.)
* the metadata for each article (authors, pubdate, journal, DOI, language, etc.)
* the fulltext content (abstract, introduction, methods, discussion, etc.)
* backmatter (references, permissions, ethics, etc.)
* non-text: tables, diagrams. images
* supplemental/supporting material
Some of this has been systematized, especially in biosciences, and the NIH (US National Institutes of Health) led to the JATS/NISO standard to create highly structured documents.

Frequently users want to search incrementally, e.g. downloading part and resuming later (especially with poor connectivity where work is often lost). Also, pygetpapers allows regular updates, e.g. weekly searches of preprint servers.

pygetpapers takes the approach of downloading once and re-analyzing later on local filestore. This saves repeated querying where connections are poor or where there is suspicion that publishers may surveil users. Moreover, publishers rarely provide more than full-text Boolean searches, whereas local tools can analyze sections and non-textual material.

We do not know of other tools which have the same functionality. curl [3] requires detailed knowledge of the download protocol. VosViewer [4] is mainly aimed at bibliography/citations.

# Overview of the architecture

## Data

The download may be repository-dependent but usually contains:
* download metadata. (query, date, errors, etc.)
* journal/article metadata. We use JATS-NISO [5] which is widely used by publishers and repository owners, especially in bioscience and medicine. There are over 200 tags. 
* fulltext. This can be 
   - XML (fulltext and metadata) 
   - images (these may not always be available)
   - tables (these are often separate)
   - PDF - usually includes the whole material but not machine-sectioned
   - HTML . often avaliable on websites
* supplemental data. This is very variable, often as PDF but also raw data files and sometimes zipped. It is not systematically arranged but `pygetpapers` allows for some heuristics.

<p align="center">
  <img src="https://user-images.githubusercontent.com/62711517/153720800-36a32046-9c92-4999-9adf-5ea34b77c29e.png" alt="pygetpapers" height="50%" width="50%">
  <h2 align="center">Fig.3 Architecture of pygetpapers</h2>
</p>

This directory structure is designed so that analysis tools can add computed data for articles

<p align="center">
  <img src="https://user-images.githubusercontent.com/62711517/153720821-d3cfdb9c-fb1b-432f-95b7-bdcc1ef6ecc0.png" alt="pygetpapers" height="50%" width="50%">
  <h2 align="center">Fig.4 Typical download directory</h2>
</p>


## Code 

### Download protocol

Most repository APIs provide a cursor-based approach to querying:
1. A query is sent and the repository creates a list of M hits (pointers to documents), sets a cursor start, and returns this information to the `pygetpapers` client.
2. The client requests a chunk of size N <= M (normally 25-1000) and the repository replies with N pointers to documents.
3. The client downloads the fulltext for each pointer (using REST) and continues until all N pointers are exhausted. 
4. The client resets the cursor mark for the next iteration. If there are no more pointers, break
5. Goto 2


The control module `pygetpapers` reads the commandline and
* Selects the repository-specific downloader
* Creates a query from user input and/or terms from dictiomaries
* Adds options and constraints
* Downloads according to protocol above, including recording progress in a metadata file

# Generic downloading concerns

* Download speeds. Excessively rapid or voluminous downloads can overload servers and are sometimes hostile (DOS). We have discussed this with major sites (EPMC, biorXiv, Crossref etc. and have a default (resettable) delay in `pygetpapers`. 
* Authentication (alerting repo to downloader header). `pygetpapers` supports anonymous, non-authenticated, access but includes a header (e.g. for Crossref)

# Design
* commandline (can be later wrapped in GUIs).
* modular (one module per repo)
* abstraction (e.g. of DATE functions)
* supports both metadata and content
* responsive to repository responses

# Mechanism of downloading
The download process for (most) servers of scientific articles is:
* create a RESTful query as URL 
* METADATA
* post query (includes optional cursor mark (units = pages), optional pagesize)
* server response is pages of hits (metadata) as XML , normally <= 1000 hits per page , (1 sec) 
* pygetpapers - incremental aggregates XML metadata as python dict in memory - small example for paper
* if cursor indicates next page, submits a query for next page, else if end terminates this part
* when finished all pages, writes metadata to CProject as JSON (total, and creates CTrees with individual metadata)
* CONTENT
* from total metadata in memory, systematically download requested (optional content) (minutes, depending on size)
* recover from crashes, restart 

# Implementation

getpapers was implemented in NodeJS which allows multithreading and therefore potentially download rates of several XML documents per second on a fast line. Installing NodeJS was a problem on some systems (especially Windows) and was not well suited for integration with scientific libraries (mainly coded in Java and Python). We, therefore, decided to rewrite in Python, keeping only the command line and output structure, and have found very easy integration with other tools, including GUIs. pygetpapers can be run both as a command-line tool and a module, which makes it versatile. 

# Interface with other tools

Downloading is naturally modular, rather slow, and we interface by writing all output to the filesystem. This means that a wide range of tools (Unix, Windows, Java, Python, etc.) can analyze and transform it. The target documents are usually static so downloads only need to be done once.
Among our own downstream tools are
* pyami - sectioning the document
* docanalysis - textual analysis and Natural Language Processing
* pyamiimage - analysis of the content of images in downloaded documents

For fulltext analysis of PDF we use GROBID and PDFBox.

# References

[1]“Systematic Reviews.” BioMed Central, 12 Feb. 2022, systematicreviewsjournal.biomedcentral.com/. Accessed 12 Feb. 2022.

[2]Wind LL, Briganti JS, Brown AM, et al. Finding What Is Inaccessible: Antimicrobial Resistance Language Use among the One Health Domains. Antibiotics (Basel, Switzerland). 2021 Apr;10(4). DOI: 10.3390/antibiotics10040385. PMID: 33916878; PMCID: PMC8065768.

[3]Hostetter, M., Kranz, D. A., Seed, C., Terman, C., & Ward, S. (1997). Curl: a gentle slope language for the Web. World Wide Web Journal, 2(2), 121–134.

[4]van Eck N. J., Waltman L. (2010) ‘ Software Survey: VOSviewer, a Computer Program for Bibliometric Mapping’, Scientometrics , 84/2: 523–38.

[5]“Standardized Markup for Journal Articles: Journal Article Tag Suite (JATS) | NISO Website.” Niso.org, 7 July 2021, www.niso.org/standards-committees/jats. Accessed 12 Feb. 2022.





