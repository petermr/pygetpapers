# pygetpapers
a Python version of getpapers 

## summary
`(py)getpapers` issues a search query to a chosen repository via its RESTful API (or by scraping), analyses the hits and systematically downloads the articles without further interaction.

## history
`getpapers` is a tool written by Rik Smith-Unna funded by ContentMine at https://github.com/ContentMine/getpapers. The OpenVirus community has a need for a Python version and Ayush Garg has written a partial implementation from scratch, with some enhancements . (2021-03) `pygetpapers` does most of what `getpapers` does.

# alphatest 2021-03
The openVirus community is asked to test the current version. Reports should be clear enough that a newcomer to `pygetpapers` can understand the purpose and operation without having to ask (`getpapers` had relativekly little documentation`). Please create wikipages for each topic and report on the following:

## Documentation
### WHAT is the purpose of pygetpapers?
This must be spelled out clearly - there has been confusion.

### HOW does pygetpapers work?
This is important because it uses remote sites and downloads information. The action has to conform to good practice. There should be an architecture diagram of the components and processes.

### WHAT resources does pygetpapers use?
What are the limitations?

### How is pygetpapers installed?

### What are the options for pygetpapers and what do they do?

### What files does pygetpapers produce?
What files? and at what stage of the operation?

## testing
### option testing
Test every optiom one-by one and record whether it does what the documentation says
### error trapping
Create deliberately incorrect inoput and test if the system traps this, whether the error messages are comprehensible and whether it leaves the filestore and machine in a clean state.

### performance
#### speed
How does `pygetpapers` compare with `getpapers`?
#### downloaded files
How do the files downloaded by `pygetpapers` correspond to `getpapers`? It may be useful to create a query with a small number of results and hence (hopefully) reproducible. Also queries with a date range so that changes in the target databases are unlikely to affer this.

### comparison with EPMC manual search.
Are the hits and downloaded files identical? 

### difficulty of use
There are certain operations, especially query formats, which cause problems. Please identify them .

### platforms
It will be important to test whether different OS give consistent results.

 
