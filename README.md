<p align="center">
  <img src="https://user-images.githubusercontent.com/62711517/117457208-93c60b00-af7b-11eb-9c00-a7077786a430.png" alt="pygetpapers" height="50%" width="50%">
  <h2 align="center">Research Papers right from python</h2>
</p>

<p>Table of Contents</p>

- [1. What is pygetpapers](#1-what-is-pygetpapers)
- [2. History](#2-history)
- [3. Formats supported by pygetpapers](#3-formats-supported-by-pygetpapers)
- [4. Architecture](#4-architecture)
- [5. About the author and community](#5-about-the-author-and-community)
- [6. Installation](#6-installation)
  - [6.1. Way one (recommended):](#61-way-one-recommended)
  - [6.2. Way two:](#62-way-two)
- [7. Usage](#7-usage)
- [8. Sample queries:](#8-sample-queries)
- [9. Contributions](#9-contributions)
- [10. Feature Requests](#10-feature-requests)
- [11. Legal Implications](#11-legal-implications)
  - [11.1. pygetpapers users should be careful to understand the law as it applies to their content mining, as they assume full responsibility for their actions when using the software.](#111-pygetpapers-users-should-be-careful-to-understand-the-law-as-it-applies-to-their-content-mining-as-they-assume-full-responsibility-for-their-actions-when-using-the-software)
  - [11.2. Countries with copyright exceptions for content mining:](#112-countries-with-copyright-exceptions-for-content-mining)
  - [11.3. Countries with proposed copyright exceptions:](#113-countries-with-proposed-copyright-exceptions)
  - [11.4. Countries with permissive interpretations of 'fair use' that might allow content mining:](#114-countries-with-permissive-interpretations-of-fair-use-that-might-allow-content-mining)
  - [11.5. General summaries and guides:](#115-general-summaries-and-guides)

# 1. What is pygetpapers


- pygetpapers is a tool to assist text miners. It makes requests to open access scientific text repositories, analyses the hits, and systematically downloads the articles without further interaction.

- It comes with the packages `pygetpapers` and `downloadtools` which provide various functions to download, process and save research papers and their metadata.

- The main medium of its interaction with users is through a command-line interface.

- `pygetpapers` has a modular design which makes maintenance easy and simple. This also allows adding support for more repositories simple.

<br>
<p>
<a href="https://github.com/petermr/pygetpapers/actions"><img src="https://github.com/petermr/pygetpapers/actions/workflows/python-package.yml/badge.svg" alt="img" width="180px" height="25px"></a>
<a href="https://github.com/petermr/pygetpapers/issues"><img src="https://img.shields.io/github/issues-raw/petermr/pygetpapers?color=blue&style=for-the-badge" alt="img" width="180px" height="30px"></a>
<a href="https://github.com/petermr/pygetpapers/issues?q=is%3Aclosed"><img src="https://img.shields.io/github/issues-closed-raw/petermr/pygetpapers?color=blue&style=for-the-badge" alt="img"  width="180px" height="30px"></a>
<a href="https://github.com/petermr/pygetpapers/commits/main"><img src="https://img.shields.io/github/last-commit/petermr/pygetpapers.svg?color=blue&style=for-the-badge" alt="img"width="180px" height="30px"></a>
<a href="https://github.com/petermr/pygetpapers/stargazers"><img src="https://img.shields.io/github/stars/petermr/pygetpapers.svg?style=social&label=Star&maxAge=2592000" alt="img"width="120px" height="30px"></a>
</p>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=petermr&repo=pygetpapers">
</p>

<p>
The developer documentation has been setup at <a href="https://pygetpapers.readthedocs.io/en/latest/#">readthedocs</a>
</p>

# 2. History

`getpapers` is a tool written by Rik Smith-Unna funded by ContentMine at https://github.com/ContentMine/getpapers. The OpenVirus community requires a Python version and Ayush Garg has written an implementation from scratch, with some enhancements.

# 3. Formats supported by pygetpapers

pygetpapers gives fulltexts in xml and pdf format. 
The metadata for papers can be saved in many formats including JSON, CSV, HTML. Queries can be saved in form of an ini configuration file. 
The additional files for papers can also be downloaded. References and citations for papers are given in XML format. 
Log files can be saved in txt format.

# 4. Architecture

<p align="center">
<img src="https://raw.githubusercontent.com/petermr/pygetpapers/main/archietecture.png" >
</p>

# 5. About the author and community

`pygetpapers` has been developed by Ayush Garg under the dear guidance of the OpenVirus community and Peter Murray Rust. Ayush is currently a high school student who believes that the world can only truly progress when knowledge is open and accessible by all.

Testers from OpenVirus have given a lot of useful feedback to Ayush without which this project would not have been possible.

The community has taken time to ensure that everyone can contribute to this project. So, YOU, the developer, reader and researcher can also contribute by testing, developing, and sharing.

# 6. Installation

Ensure that `pip` is installed along with python. Download python from: https://www.python.org/downloads/ and select the option Add Python to Path while installing.

Check out https://pip.pypa.io/en/stable/installing/ if difficulties installing pip.

<hr>

## 6.1. Way one (recommended):

- Ensure git cli is installed and is available in path. Check out (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

- Enter the command: `pip install git+git://github.com/petermr/pygetpapers`

- Ensure pygetpapers has been installed by reopening the terminal and typing the command `pygetpapers`

- You should see a help message come up.

<hr>

## 6.2. Way two:

- Manually clone the repository and run `python setup.py install` from inside the repository directory

- Ensure pygetpapers has been installed by reopening the terminal and typing the command `pygetpapers`

- You should see a help message come up.

<hr>

# 7. Usage

- Type the command `pygetpapers` to run the help.

```
usage: pygetpapers [-h] [--config CONFIG] [-v] [-q QUERY] [-o OUTPUT]
                   [--save_query] [-x] [-p] [-s] [--references REFERENCES]
                   [-n] [--citations CITATIONS] [-l LOGLEVEL] [-f LOGFILE]
                   [-k LIMIT] [-r RESTART] [-u UPDATE] [--onlyquery] [-c]
                   [--makehtml] [--synonym] [--startdate STARTDATE]
                   [--enddate ENDDATE]

Welcome to Pygetpapers version 0.0.4. -h or --help for help

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       config file path to read query for pygetpapers
  -v, --version         output the version number
  -q QUERY, --query QUERY
                        query string transmitted to repository API. Eg.
                        "Artificial Intelligence" or "Plant Parts". To escape
                        special characters within the quotes, use backslash.
                        Incase of nested quotes, ensure that the initial
                        quotes are double and the qutoes inside are single.
                        For eg: `'(LICENSE:"cc by" OR LICENSE:"cc-by") AND
                        METHODS:"transcriptome assembly"' ` is wrong. We
                        should instead use `"(LICENSE:'cc by' OR LICENSE:'cc-
                        by') AND METHODS:'transcriptome assembly'"`
  -o OUTPUT, --output OUTPUT
                        output directory (Default: Folder inside current
                        working directory named )
  --save_query          saved the passed query in a config file
  -x, --xml             download fulltext XMLs if available
  -p, --pdf             download fulltext PDFs if available
  -s, --supp            download supplementary files if available
  --references REFERENCES
                        Download references if available. Requires source for
                        references (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).
  -n, --noexecute       report how many results match the query, but don't
                        actually download anything
  --citations CITATIONS
                        Download citations if available. Requires source for
                        citations (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).
  -l LOGLEVEL, --loglevel LOGLEVEL
                        Provide logging level. Example --log warning
                        <<info,warning,debug,error,critical>>, default='info'
  -f LOGFILE, --logfile LOGFILE
                        save log to specified file in output directory as well
                        as printing to terminal
  -k LIMIT, --limit LIMIT
                        maximum number of hits (default: 100)
  -r RESTART, --restart RESTART
                        Reads the json and makes the xml files. Takes the path
                        to the json as the input
  -u UPDATE, --update UPDATE
                        Updates the corpus by downloading new papers. Takes
                        the path of metadata json file of the orignal corpus
                        as the input. Requires -k or --limit (If not provided,
                        default will be used) and -q or --query (must be
                        provided) to be given. Takes the path to the json as
                        the input.
  --onlyquery           Saves json file containing the result of the query in
                        storage. The json file can be given to --restart to
                        download the papers later.
  -c, --makecsv         Stores the per-document metadata as csv.
  --makehtml            Stores the per-document metadata as html.
  --synonym             Results contain synonyms as well.
  --startdate STARTDATE
                        Gives papers starting from given date. Format: YYYY-
                        MM-DD
  --enddate ENDDATE     Gives papers till given date. Format: YYYY-MM-DD

Args that start with '--' (eg. -v) can also be set in a config file (specified
via --config). Config file syntax allows: key=value, flag=true, stuff=[a,b,c]
(for details, see syntax at https://goo.gl/R74nmi). If an arg is specified in
more than one place, then command line values override config file values which
override defaults.
```

Queries are build using `-q` flag. The query format can be found at http://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf A condensed guide can be found at https://github.com/petermr/pygetpapers/wiki/query-format

# 8. Sample queries:

1. The following query downloads 100 full-text XML, pdfs, and supplementary files along with the CSV and JSON(default) for the topic "lantana" and saves them in a directory called "test".

   `pygetpapers -q "lantana" -k 100 -o "test" --supp -c -p -x`

   ![1](https://user-images.githubusercontent.com/70321942/116696048-03b61d80-a9df-11eb-8bb2-6190aef8a6db.PNG)

2. The following query just prints out the number of hits for the topic `lantana`

   `pygetpapers -n -q "lantana"`

   ![n](https://user-images.githubusercontent.com/70321942/116695234-ef255580-a9dd-11eb-96d1-a01841a5af21.PNG)

3. The following query just creates the CSV output for metadata of 100 papers on the topic `lantana` in an output directory called "test"

   `pygetpapers --onlyquery -q "lantana" -k 100 -o "test" -c`

   ![3](https://user-images.githubusercontent.com/70321942/116697221-8c818900-a9e0-11eb-8a29-5414314b415d.PNG)



4. If the user wants to update an existing corpus in the directory test which has eupmc_resuts.json with 100 papers of query `lantana` along with their XML files and pdfs, the following query can be used:

   `pygetpapers --update "C:\Users\DELL\test\eupmc_results.JSON" -q "lantana" -k 10 -x -p`

5. If the user wants to download pdfs for a corpus in the directory test which has eupmc_resuts.json which originally only had XML files, or the query broke in between and they want to restart the download of pdfs and XML, they can use the following query

   `pygetpapers --restart "C:\Users\DELL\test\eupmc_results.json" -o "test" -x -p -q "lantana"`

   ![5](https://user-images.githubusercontent.com/70321942/116698739-58a76300-a9e2-11eb-8b56-1fd177bf9b1c.PNG)

6. If the user wants references then the following query download references.xml file if available. Requires source for references (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR)

   `pygetpapers -q "lantana" -k 10 -o "test" -c -x --references PMC`

   ![rrr](https://user-images.githubusercontent.com/70321942/116775022-0f0c5600-aa7e-11eb-9625-eaddd53f9aca.PNG)

   ![rr](https://user-images.githubusercontent.com/70321942/116774866-1848f300-aa7d-11eb-907c-259e2047de69.PNG)

7. if the user wants a synonym then `--synonym` provides results that contain synonyms as well

   `pygetpapers --onlyquery -q "lantana" -k 10 -o "test" -c --synonym`

   ![s](https://user-images.githubusercontent.com/70321942/116773871-116ab200-aa76-11eb-962a-8cdd6366cc17.PNG)

8. if the user wants to save the query to use it later
    `pygetpapers -q "lantana" --save_query`

9. if user wants to get papers within a date range
    `pygetpapers -q "lantana" --startdate "2020-01-02" --enddate "2021-09-09"`

10. if the user wants to start query from a configuration file
    `pygetpapers --config "C:\Users\DELL\test\saved_config.ini"`


# 9. Contributions

Contributions are welcome through issues as well as pull requests. For direct contributions, you can mail the author at ayush@science.org.in.

# 10. Feature Requests

To request features, please put them in issues

# 11. Legal Implications

## 11.1. pygetpapers users should be careful to understand the law as it applies to their content mining, as they assume full responsibility for their actions when using the software.

## 11.2. Countries with copyright exceptions for content mining:

- UK
- Japan

## 11.3. Countries with proposed copyright exceptions:

- Ireland
- EU countries 

## 11.4. Countries with permissive interpretations of 'fair use' that might allow content mining:

- Israel
- USA
- Canada

## 11.5. General summaries and guides:

- _"The legal framework of text and data mining (TDM)"_, carried out for the European Commission in March 2014 ([PDF](http://ec.europa.eu/internal_market/copyright/docs/studies/1403_study2_en.pdf))
- _"Standardisation in the area of innovation and technological development, notably in the field of Text and Data Mining"_, carried out for the European Commission in 2014 ([PDF](http://ec.europa.eu/research/innovation-union/pdf/TDM-report_from_the_expert_group-042014.pdf))
