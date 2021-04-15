# pygetpapers

a Python version of getpapers


[![Build Status](https://travis-ci.org/petermr/pygetpapers.png?branch=master)](https://travis-ci.org/petermr/pygetpapers)
## Contributing [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/petermr/pygetpapers/issues)
[![HitCount](http://hits.dwyl.com/petermr/pygetpapers.svg)](http://hits.dwyl.com/petermr/pygetpapers)



## summary

`(py)getpapers` issues a search query to a chosen repository via its RESTful API (or by scraping), analyses the hits and systematically downloads the articles without further interaction.

## history

`getpapers` is a tool written by Rik Smith-Unna funded by ContentMine at https://github.com/ContentMine/getpapers. The OpenVirus community has a need for a Python version and Ayush Garg has written a implementation from scratch, with some enhancements . `pygetpapers` does most of what `getpapers` does.

## Documentation

### Installation

Ensure that `pip` is installed along with python. Download python from: https://www.python.org/downloads/ and select the option Add Python to Path while installing.

Check out https://pip.pypa.io/en/stable/installing/ if difficulties installing pip.

Way one (recommended): Ensure git cli is installed and is available in path. Check out (https://git-scm.com/)
Enter the command: `pip install git+git://github.com/petermr/pygetpapers`

    Ensure pygetpapers has been installed by reopening terminal and typing the command `pygetpapers`

    You should see a help message come up.

Way two:
Manually clone the repository and run `python setup.py install` from inside the repository directory

    Ensure pygetpapers has been installed by reopening terminal and typing the command `pygetpapers`

    You should see a help message come up.

### Usage

Type the command `pygetpapers` to run the help.

This is the help message:

    ```
    usage: pygetpapers [-h] [-v] [-q QUERY] [-o OUTPUT] [-x] [-p] [-s]
                    [--references REFERENCES] [-n] [--citations CITATIONS]
                    [-l LOGLEVEL] [-f LOGFILE] [-k LIMIT] [-r RESTART]
                    [-u UPDATE] [--onlyquery] [-c] [--synonym]

    Welcome to Pygetpapers version <pygetpapers version> -h or --help for help

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         output the version number
    -q QUERY, --query QUERY
                            query string transmitted to repository API. Eg.
                            'Artificial Intelligence' or 'Plant Parts'. To escape
                            special characters within the quotes, use backslash.
                            The query to be quoted in either single or double
                            quotes.
    -o OUTPUT, --output OUTPUT
                            output directory (Default: current working directory)
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
    -c, --makecsv         Stores the per-document metadata as csv. Works only
                            with --api method.
    --synonym             Results contain synonyms as well.

    ```

Queries are build using `-q` flag. The query format can be found at https://github.com/petermr/pygetpapers/wiki/query-format

Sample queries:

1. The following query downloads 100 full text xmls, pdfs and supplementary files along with the csv and json(default) for the topic "lantana" and saves them in a directory called "test".

`pygetpapers -q "lantana" -k 100 -o "test" --supp -c -p -x`

2. The following query just prints out the number of hits for the topic `lantana`

`pygetpapers -n -q "lantana"`

3. The following query just creates the csv output for metadata of 100 papers on the topic `lantana` in an output directory called "test"

`pygetpapers --onlyquery -q "lantana" -k 100 -o "test" -c`

4. If the user wants to update an existing corpus in the directory test2 which has eupmc_resuts.json with 100 papers of query `lantana` along with their xmls and pdfs, the following query can be used:

`pygetpapers --update "D:\main_projects\test2\test\eupmc_results.json" -q "lantana" -k 100 -x -p`

5. If user wants to download pdfs for a corpus in the directory test2 which has eupmc_resuts.json which originally only had xmls, or the query broke in between and they want to restart the download of pdfs and xmls, they can use the following query

`pygetpapers --restart "D:\main_projects\test2\test\eupmc_results.json" -o "test" -x -p -q "lantana"`

### Contribution

Contributions are welcome through issues as well as pull requests. For direct contributions you can mail the authon Ayush Garg at ayush@science.org.in

### Feature Requests

To request features, please put them in issues
