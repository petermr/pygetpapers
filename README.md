# pygetpapers
### Summary
- a Python version of getpapers
- `(py)getpapers` issues a search query to a chosen repository via its RESTful API (or by scraping), analyses the hits and systematically downloads the articles without further interaction.

### Installation

Ensure that `pip` is installed along with python. Download python from: https://www.python.org/downloads/ and select the option Add Python to Path while installing.

Check out https://pip.pypa.io/en/stable/installing/ if difficulties installing pip.

Way one (recommended): Ensure git cli is installed and is available in path. Check out (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
Enter the command: `pip install git+git://github.com/petermr/pygetpapers`

    Ensure pygetpapers has been installed by reopening terminal and typing the command `pygetpapers`

    You should see a help message come up.

Way two:
Manually clone the repository and run `python setup.py install` from inside the repository directory

    Ensure pygetpapers has been installed by reopening terminal and typing the command `pygetpapers`

    You should see a help message come up.
### Usage
- Type the command `pygetpapers` to run the help.

![help](https://user-images.githubusercontent.com/70321942/116694877-70c8b380-a9dd-11eb-9dfa-48cf8632bee5.PNG)

Queries are build using `-q` flag. The query format can be found at http://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf A condensed guide can be found at https://github.com/petermr/pygetpapers/wiki/query-format

### Sample queries:

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


### Contribution

Contributions are welcome through issues as well as pull requests. For direct contributions you can mail the authon Ayush Garg at ayush@science.org.in

### Feature Requests

To request features, please put them in issues
