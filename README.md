# pygetpapers

## What is pygetpapers

- pygetpapers is a tool to assit text miners. It makes requests to open access scientific text repositories, analyses the hits and systematically downloads the articles without further interaction.

- It comes with the packages `pygetpapers` and `downloadtools` which provide various fuctions to download, process and save research papers and their metadata.

- The main medium of its interaction with users is through a command line interface.

- `pygetpapers` has a modular design which makes maintainance easy and simple. This also allows adding support for more repositories simple.

## GitHub

<p align="center">
<a href="https://github.com/petermr/pygetpapers/issues"><img src="https://img.shields.io/github/issues-raw/petermr/pygetpapers?color=blue&style=for-the-badge" alt="img" width="180px"></a>
<a href="https://github.com/petermr/pygetpapers/issues?q=is%3Aclosed"><img src="https://img.shields.io/github/issues-closed-raw/petermr/pygetpapers?color=blue&style=for-the-badge" alt="img"  width="200px"></a>
<a href="https://github.com/petermr/pygetpapers/commits/main"><img src="https://img.shields.io/github/last-commit/petermr/pygetpapers.svg?color=blue&style=for-the-badge" alt="img"width="200px"></a>
<a href="https://github.com/petermr/pygetpapers/stargazers"><img src="https://img.shields.io/github/stars/petermr/pygetpapers.svg?style=social&label=Star&maxAge=2592000" alt="img"width="140x"></a>
</p>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api/pin/?username=petermr&repo=pygetpapers">
</p>

## History

`getpapers` is a tool written by Rik Smith-Unna funded by ContentMine at https://github.com/ContentMine/getpapers. The OpenVirus community has a need for a Python version and Ayush Garg has written an implementation from scratch, with some enhancements.

## Installation

Ensure that `pip` is installed along with python. Download python from: https://www.python.org/downloads/ and select the option Add Python to Path while installing.

Check out https://pip.pypa.io/en/stable/installing/ if difficulties installing pip.

<hr>

### Way one (recommended):

- Ensure git cli is installed and is available in path. Check out (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

- Enter the command: `pip install git+git://github.com/petermr/pygetpapers`

- Ensure pygetpapers has been installed by reopening terminal and typing the command `pygetpapers`

- You should see a help message come up.

<hr>

### Way two:

- Manually clone the repository and run `python setup.py install` from inside the repository directory

- Ensure pygetpapers has been installed by reopening terminal and typing the command `pygetpapers`

- You should see a help message come up.

<hr>

## Usage

- Type the command `pygetpapers` to run the help.

![help](https://user-images.githubusercontent.com/70321942/116694877-70c8b380-a9dd-11eb-9dfa-48cf8632bee5.PNG)

Queries are build using `-q` flag. The query format can be found at http://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf A condensed guide can be found at https://github.com/petermr/pygetpapers/wiki/query-format

## Sample queries:

1. The following query downloads 100 full text xmls, pdfs and supplementary files along with the csv and json(default) for the topic "lantana" and saves them in a directory called "test".

   `pygetpapers -q "lantana" -k 100 -o "test" --supp -c -p -x`

   ![1](https://user-images.githubusercontent.com/70321942/116696048-03b61d80-a9df-11eb-8bb2-6190aef8a6db.PNG)

2. The following query just prints out the number of hits for the topic `lantana`

   `pygetpapers -n -q "lantana"`

   ![n](https://user-images.githubusercontent.com/70321942/116695234-ef255580-a9dd-11eb-96d1-a01841a5af21.PNG)

3. The following query just creates the csv output for metadata of 100 papers on the topic `lantana` in an output directory called "test"

   `pygetpapers --onlyquery -q "lantana" -k 100 -o "test" -c`

   ![3](https://user-images.githubusercontent.com/70321942/116697221-8c818900-a9e0-11eb-8a29-5414314b415d.PNG)

4. If the user wants to update an existing corpus in the directory test which has eupmc_resuts.json with 100 papers of query `lantana` along with their xmls and pdfs, the following query can be used:

   `pygetpapers --update "C:\Users\DELL\test\eupmc_results.json" -q "lantana" -k 10 -x -p`

5. If user wants to download pdfs for a corpus in the directory test2 which has eupmc_resuts.json which originally only had xmls, or the query broke in between and they want to restart the download of pdfs and xmls, they can use the following query

   `pygetpapers --restart "C:\Users\DELL\test\eupmc_results.json" -o "test" -x -p -q "lantana"`

   ![5](https://user-images.githubusercontent.com/70321942/116698739-58a76300-a9e2-11eb-8b56-1fd177bf9b1c.PNG)

6. If the user wants to update an existing corpus in the directory test which has eupmc_resuts.json with 100 papers of query `lantana` along with their xmls and pdfs, the following query can be used:

   `pygetpapers --update "C:\Users\DELL\test\eupmc_results.json" -q "lantana" -k 10 -x -p`

7. If user wants to download pdfs for a corpus in the directory test which has eupmc_resuts.json which originally only had xmls, or the query broke in between and they want to restart the download of pdfs and xmls, they can use the following query

   `pygetpapers --restart "C:\Users\DELL\test\eupmc_results.json" -o "test" -x -p -q "lantana"`

   ![5](https://user-images.githubusercontent.com/70321942/116698739-58a76300-a9e2-11eb-8b56-1fd177bf9b1c.PNG)

8. If user wants references then following query download references.xml file if available. Requires source for references (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR)

   `pygetpapers -q "lantana" -k 10 -o "test" -c -x --references PMC`

   ![rrr](https://user-images.githubusercontent.com/70321942/116775022-0f0c5600-aa7e-11eb-9625-eaddd53f9aca.PNG)

   ![rr](https://user-images.githubusercontent.com/70321942/116774866-1848f300-aa7d-11eb-907c-259e2047de69.PNG)

9. if user wants synonym then `--synonym` provides results which contain synonyms as well

   `pygetpapers --onlyquery -q "lantana" -k 10 -o "test" -c --synonym`

   ![s](https://user-images.githubusercontent.com/70321942/116773871-116ab200-aa76-11eb-962a-8cdd6366cc17.PNG)

10. if user wants to save the query to use it later
    `pygetpapers -q "lantana" --save_query`

11. if user wants to get papers within a date range
    `pygetpapers -q "lantana" --startdate "2020-01-02" --enddate "2021-09-09"`

12. if user wants to start query from configuration file
    `pygetpapers --config "C:\Users\DELL\test\saved_config.ini"`

## About the author and community

`pygetpapers` has been developed by Ayush Garg under the dear guidance of the OpenVirus community and Peter Murray Rust. Ayush is currently a high school student who believes that the world can only truly progress when knowledge is open and accessible by all.

Testers from OpenVirus have given a lot of useful feedback to Ayush without which this project would not have been possible.

The community has taken time to ensure that everyone can contribute to this project. So, YOU, the developer, reader and researcher can also contribute by testing, developing and sharing.

## Contributions

Contributions are welcome through issues as well as pull requests. For direct contributions you can mail the author at ayush@science.org.in.

## Feature Requests

To request features, please put them in issues

# pygetpapers users should be careful to understand the law as it applies to their content mining, as they assume full responsibility for their actions when using the software.

## Countries with copyright exceptions for content mining:

- UK
- Japan

## Countries with proposed copyright exceptions:

- Ireland
- EU

## Countries with permissive interpretations of 'fair use' that might allow content mining:

- Israel
- USA
- Canada

## General summaries and guides:

- _"The legal framework of text and data mining (TDM)"_, carried out for the European Commission in March 2014 ([PDF](http://ec.europa.eu/internal_market/copyright/docs/studies/1403_study2_en.pdf))
- _"Standardisation in the area of innovation and technological development, notably in the field of Text and Data Mining"_, carried out for the European Commission in 2014 ([PDF](http://ec.europa.eu/research/innovation-union/pdf/TDM-report_from_the_expert_group-042014.pdf))
