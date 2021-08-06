What is pygetpapers
======================

.. figure:: https://user-images.githubusercontent.com/62711517/117457208-93c60b00-af7b-11eb-9c00-a7077786a430.png
   :alt: pygetpapers

-  pygetpapers is a tool to assist text miners. It makes requests to
   open access scientific text repositories, analyses the hits, and
   systematically downloads the articles without further interaction.

-  It comes with the packages ``pygetpapers`` and ``downloadtools``
   which provide various functions to download, process and save
   research papers and their metadata.

-  The main medium of its interaction with users is through a
   command-line interface.

-  ``pygetpapers`` has a modular design which makes maintenance easy and
   simple. This also allows adding support for more repositories simple.

.. raw:: html

   <p>

.. raw:: html

   </p>

   <p align="center">
     

.. raw:: html

   </p>

   <p>

The developer documentation has been setup at readthedocs

.. raw:: html

   </p>

2. History
==========

``getpapers`` is a tool written by Rik Smith-Unna funded by ContentMine
at https://github.com/ContentMine/getpapers. The OpenVirus community
requires a Python version and Ayush Garg has written an implementation
from scratch, with some enhancements.

3. Formats supported by pygetpapers
===================================

-  pygetpapers gives fulltexts in xml and pdf format.
-  The metadata for papers can be saved in many formats including JSON,
   CSV, HTML.
-  Queries can be saved in form of an ini configuration file.
-  The additional files for papers can also be downloaded. References
   and citations for papers are given in XML format.
-  Log files can be saved in txt format.

4. Architecture
===============

.. raw:: html

   <p align="center">

.. raw:: html

   </p>

5. About the author and community
=================================

``pygetpapers`` has been developed by Ayush Garg under the dear guidance
of the OpenVirus community and Peter Murray Rust. Ayush is currently a
high school student who believes that the world can only truly progress
when knowledge is open and accessible by all.

Testers from OpenVirus have given a lot of useful feedback to Ayush
without which this project would not have been possible.

The community has taken time to ensure that everyone can contribute to
this project. So, YOU, the developer, reader and researcher can also
contribute by testing, developing, and sharing.

6. Installation
===============

Ensure that ``pip`` is installed along with python. Download python
from: https://www.python.org/downloads/ and select the option Add Python
to Path while installing.

Check out https://pip.pypa.io/en/stable/installing/ if difficulties
installing pip.

.. raw:: html

   <hr>

6.1. Method one (recommended):
------------------------------

-  Ensure git cli is installed and is available in path. Check out
   (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

-  Enter the command:
   ``pip install git+git://github.com/petermr/pygetpapers``

-  Ensure pygetpapers has been installed by reopening the terminal and
   typing the command ``pygetpapers``

-  You should see a help message come up.

.. raw:: html

   <hr>

6.2. Method two:
----------------

-  Manually clone the repository and run ``python setup.py install``
   from inside the repository directory

-  Ensure pygetpapers has been installed by reopening the terminal and
   typing the command ``pygetpapers``

-  You should see a help message come up.

.. raw:: html

   <hr>

7. Usage
========

``pygetpapers`` is a commandline tool. You can ask for help by running:

::

    pygetpapers --help

::

    usage: pygetpapers [-h] [--config CONFIG] [-v] [-q QUERY] [-o OUTPUT] [--save_query] [-x] [-p] [-s] [-z]
                       [--references REFERENCES] [-n] [--citations CITATIONS] [-l LOGLEVEL] [-f LOGFILE] [-k LIMIT]
                       [-r RESTART] [-u UPDATE] [--onlyquery] [-c] [--makehtml] [--synonym] [--startdate STARTDATE]
                       [--enddate ENDDATE] [--terms TERMS] [--api API] [--filter FILTER]

    Welcome to Pygetpapers version 0.0.6.3. -h or --help for help

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       config file path to read query for pygetpapers
      -v, --version         output the version number
      -q QUERY, --query QUERY
                            query string transmitted to repository API. Eg. "Artificial Intelligence" or "Plant Parts". To
                            escape special characters within the quotes, use backslash. Incase of nested quotes, ensure
                            that the initial quotes are double and the qutoes inside are single. For eg: `'(LICENSE:"cc
                            by" OR LICENSE:"cc-by") AND METHODS:"transcriptome assembly"' ` is wrong. We should instead
                            use `"(LICENSE:'cc by' OR LICENSE:'cc-by') AND METHODS:'transcriptome assembly'"`
      -o OUTPUT, --output OUTPUT
                            output directory (Default: Folder inside current working directory named )
      --save_query          saved the passed query in a config file
      -x, --xml             download fulltext XMLs if available
      -p, --pdf             download fulltext PDFs if available
      -s, --supp            download supplementary files if available
      -z, --zip             download files from ftp endpoint if available
      --references REFERENCES
                            Download references if available. Requires source for references
                            (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).
      -n, --noexecute       report how many results match the query, but don't actually download anything
      --citations CITATIONS
                            Download citations if available. Requires source for citations
                            (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR).
      -l LOGLEVEL, --loglevel LOGLEVEL
                            Provide logging level. Example --log warning <<info,warning,debug,error,critical>>,
                            default='info'
      -f LOGFILE, --logfile LOGFILE
                            save log to specified file in output directory as well as printing to terminal
      -k LIMIT, --limit LIMIT
                            maximum number of hits (default: 100)
      -r RESTART, --restart RESTART
                            Reads the json and makes the xml files. Takes the path to the json as the input
      -u UPDATE, --update UPDATE
                            Updates the corpus by downloading new papers. Takes the path of metadata json file of the
                            orignal corpus as the input. Requires -k or --limit (If not provided, default will be used)
                            and -q or --query (must be provided) to be given. Takes the path to the json as the input.
      --onlyquery           Saves json file containing the result of the query in storage. The json file can be given to
                            --restart to download the papers later.
      -c, --makecsv         Stores the per-document metadata as csv.
      --makehtml            Stores the per-document metadata as html.
      --synonym             Results contain synonyms as well.
      --startdate STARTDATE
                            Gives papers starting from given date. Format: YYYY-MM-DD
      --enddate ENDDATE     Gives papers till given date. Format: YYYY-MM-DD
      --terms TERMS         Location of the txt file which contains terms serperated by a comma which will beOR'ed among
                            themselves and AND'ed with the query
      --api API             API to search [eupmc, crossref,arxiv,biorxiv,medrxiv,rxivist-bio,rxivist-med] (default: eupmc)
      --filter FILTER       filter by key value pair, passed straight to the crossref api only

Queries are build using ``-q`` flag. The query format can be found at
http://europepmc.org/docs/EBI\_Europe\_PMC\_Web\_Service\_Reference.pdf
A condensed guide can be found at
https://github.com/petermr/pygetpapers/wiki/query-format

8. What is CProject?
====================

A CProject is a directory structure that the AMI toolset uses to gather
and process data. Each paper gets its folder. A CTree is a subdirectory
of a CProject that deals with a single paper.

9. Tutorial
===========

``pygetpapers`` was on version ``0.0.6.4.`` when the tutorials were
documented.

``pygetpapers`` supports multiple APIs including eupmc,
crossref,arxiv,biorxiv,medrxiv,rxivist-bio,rxivist-med. By default, it
queries EPMC. You can specify the API by using ``--api`` flag.

+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| Features           | EPMC              | crossref         | arxiv   | biorxiv           | medarxiv          | rxvist            |
+====================+===================+==================+=========+===================+===================+===================+
| Fulltext formats   | xml, pdf          | NA               | NA      | xml               | xml               | xml               |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| Metdata formats    | json, html, csv   | json, xml, csv   | json    | json, csv, html   | json, csv, html   | json, html, csv   |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| ``--query``        | yes               | yes              | yes     | NA                | NA                | NA                |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| ``--update``       | yes               | NA               | NA      | yes               | yes               |                   |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| ``--restart``      | yes               |                  |         |                   |                   |                   |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| ``--citation``     | yes               | NA               | NA      | NA                | NA                | NA                |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| ``--references``   | yes               | NA               | NA      | NA                | NA                | NA                |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+
| ``--terms``        | yes               | yes              | yes     | NA                | NA                | NA                |
+--------------------+-------------------+------------------+---------+-------------------+-------------------+-------------------+

9.1. EPMC (Default API)
-----------------------

9.1.1. Example Query
~~~~~~~~~~~~~~~~~~~~

Let's break down the following query:

::

    pygetpapers -q "METHOD: invasive plant species" -k 10 -o "invasive_plant_species_test" -c --makehtml -x --save_query

+------------------+--------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| Flag             | What it does                                           | In this case ``pygetpapers``...                                                                                 |
+==================+========================================================+=================================================================================================================+
| ``-q``           | specifies the query                                    | queries for 'essential oil' in METHODS section                                                                  |
+------------------+--------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``-k``           | number of hits (default 100)                           | limits hits to 30                                                                                               |
+------------------+--------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``-o``           | specifies output directory                             | outputs to essential\_oil\_30                                                                                   |
+------------------+--------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``-x``           | downloads fulltext xml                                 |                                                                                                                 |
+------------------+--------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``-c``           | downloads per-paper metadata into a single csv         | downloads single CSV named ```europe_pmc.csv`` <resources/invasiv_plant_species_test/europe_pmc.csv>`__         |
+------------------+--------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| ``--makehtml``   | downloads per-paper metadata into a single HTML file   | downloads single HTML named ```europe_pmc.html`` <resources/invasiv_plant_species_test/eupmc_results.html>`__   |
+------------------+--------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+

``pygetpapers``, by default, writes metadata to a JSON file within: -
individual paper directory for corresponding paper
(``epmc_result.json``) - working directory for all downloaded papers
(```epmc_results.json`` <resources/invasiv_plant_species_test/eupmc_results.json>```__)

OUTPUT:

::

    INFO: Final query is METHOD: invasive plant species
    INFO: Total Hits are 17910
    0it [00:00, ?it/s]WARNING: Keywords not found for paper 1
    WARNING: Keywords not found for paper 4
    1it [00:00, 164.87it/s]
    INFO: Saving XML files to C:\Users\shweata\invasive_plant_species_test\*\fulltext.xml
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:21<00:00,  2.11s/it]

9.1.2. Scope the number of hits for a query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are just scoping the number of hits for a given query, you can
use ``-n`` flag as shown below.

``pygetpapers -n -q "essential oil"`` OUTPUT:

::

    INFO: Final query is essential oil
    INFO: Total number of hits for the query are 190710

9.1.3. Update an existing CProject with **new papers** by feeding the metadata JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--update`` command is used to update a CProject with a new set of
papers on same or different query. If let's say you have a corpus of a
30 papers on 'essential oil' (like before) and would like to download 20
more papers to the same CProject directory, you use ``--update``
command.

``--update`` flags takes the ``eupmc_results.JSON``'s absolute path
present in the CProject directory. INPUT:

::

    pygetpapers --update "C:\Users\shweata\essential_oil_30_1\eupmc_results.JSON" -q "lantana" -k 20 -x

OUTPUT:

::

    INFO: Final query is lantana
    INFO: Total Hits are 1909
    0it [00:00, ?it/s]WARNING: html url not found for paper 1
    WARNING: pdf url not found for paper 1
    WARNING: Keywords not found for paper 2
    WARNING: Keywords not found for paper 3
    WARNING: Author list not found for paper 5
    WARNING: Author list not found for paper 8
    WARNING: Keywords not found for paper 9
    WARNING: Keywords not found for paper 11
    WARNING: Keywords not found for paper 19
    1it [00:00, 216.37it/s]
    INFO: Saving XML files to C:\Users\shweata\essential_oil_30_1\*\fulltext.xml
    100%|██████████████████████████████████████████████████████████████████████████████████| 50/50 [01:28<00:00,  1.78s/it]

9.1.3.1. How is ``--update`` different from just downloading x number of papers to the same output directory?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By using ``--update`` command you can be sure that there are no
duplicate papers. You can't be sure when you just download x number of
papers to the output directory. ### 9.1.4. Restart downloading papers to
an existing CProject ``--restart`` flag can be used for two purposes:
-To download papers in different format. Let's say you downloaded XMLs
in the first round. If you want to download pdfs for same set of papers,
you use this flag. - Continue the download from the stage where it
broke. This feature would particularly come in handy if you are on poor
lines. You can resume downloading at whatever stage you cut off by using
the ``update`` flag as we've described. ``--restart`` flag takes in the
absolute path of the ``JSON`` metadata file.

``pygetpapers --restart "C:\Users\shweata\essential_oil_30_1\eupmc_results.JSON" -q "lantana" -x -p``

.. figure:: https://user-images.githubusercontent.com/70321942/116698739-58a76300-a9e2-11eb-8b56-1fd177bf9b1c.PNG
   :alt: 5

   5
9.1.4.1. Difference between ``--restart`` and ``--update``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  If you aren't looking download new set of papers but would want to
   download a papers in different format for existing papers,
   ``--restart`` is the flag you'd want to use
-  If you are looking to download a new set of papers to an existing
   Cproject, then you'd use ``--update`` command. You should note that
   the format in which you download papers would only apply to the new
   set of papers and not for the old.

9.1.5. Downloading citations and references for papers, if available
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``--references`` and ``--citations`` flags can be used to download
   the references and citations respectively.
-  It also requires source for references
   (AGR,CBA,CTX,ETH,HIR,MED,PAT,PMC,PPR)

``pygetpapers -q "lantana" -k 10 -o "test" -c -x --citation PMC``

9.1.6. 9.1.6.Downloading only the metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are looking to download just the metadata in the supported
formats\ ``--onlyquery`` is the flag you use. It saves the metadata in
the output directory.

You can use ``--restart`` feature to download the fulltexts for these
papers. INPUT:

::

    pygetpapers --onlyquery -q "lantana" -k 10 -o "lantana_test" -c

OUTPUT:

::

    INFO: Final query is lantana
    INFO: Total Hits are 1909
    0it [00:00, ?it/s]WARNING: html url not found for paper 1
    WARNING: pdf url not found for paper 1
    WARNING: Keywords not found for paper 2
    WARNING: Keywords not found for paper 3
    WARNING: Author list not found for paper 5
    WARNING: Author list not found for paper 8
    WARNING: Keywords not found for paper 9
    1it [00:00, 407.69it/s]

9.1.7. Download papers within certain start and end date range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By using ``--startdate`` and ``--enddate`` you can specify the date
range within which the papers you want to download were first published.

::

    pygetpapers -q "METHOD:essential oil" --startdate "2020-01-02" --enddate "2021-09-09"

9.1.8. Saving query for later use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To save a query for later use, you can use ``--save_query``. What it
does is that it saves the query in a ``.ini`` file in the output
directory.

::

    pygetpapers -q "lantana" -k 10 -o "lantana_query_config"--save_query

`Here <resources/invasive_plant_species_test/saved_config.ini>`__ is an
example config file ``pygetpapers`` outputs ### 9.1.9. Feed query using
``config.ini`` file Using can use the ``config.ini`` file you created
using ``--save_query``, you re-run the query. To do so, you will give
``--config`` flag the absolute path of the ``saved_config.ini`` file.

``pygetpapers --config "C:\Users\shweata\lantana_query_config\saved_config.ini"``

9.1.10. Querying using a term list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your query is complex with multiple ORs, you can use ``--terms``
feature. To use this, you will: - Create a ``.txt`` file with list of
terms separated by commas. - Give the ``--terms`` flag the absolute path
of the ``.txt`` file

``-q`` is optional.The terms would be OR'ed with each other ANDed with
the query, if given.

INPUT:

::

    pygetpapers -q "essential oil" --terms C:\Users\shweata\essential_oil_terms.txt -k 10 -o "terms_test_essential_oil" -x  

OUTPUT:

::

    C:\Users\shweata>pygetpapers -q "essential oil" --terms C:\Users\shweata\essential_oil_terms.txt -k 10 -o "terms_test_essential_oil"
    INFO: Final query is (essential oil AND (antioxidant OR  antibacterial OR  antifungal OR  antiseptic OR  antitrichomonal agent))
    INFO: Total Hits are 43397
    0it [00:00, ?it/s]WARNING: Author list not found for paper 9
    1it [00:00, 1064.00it/s]
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:19<00:00,  1.99s/it]

You can also use this feature to download papers by using the PMC Ids.
You can feed the ``.txt`` file with PMC ids comman-separated. Make sure
to give a large enough hit number to download all the papers specified
in the text file.

Example text file can be found,
`here <resources/essential_oil_terms.txt>`__ INPUT:

::

    pygetpapers --terms C:\Users\shweata\PMCID_pygetpapers_text.txt -k 100 -o "PMCID_test"

OUTPUT:

::

    INFO: Final query is (PMC6856665 OR  PMC6877543 OR  PMC6927906 OR  PMC7008714 OR  PMC7040181 OR  PMC7080866 OR  PMC7082878 OR  PMC7096589 OR  PMC7111464 OR  PMC7142259 OR  PMC7158757 OR  PMC7174509 OR  PMC7193700 OR  PMC7198785 OR  PMC7201129 OR  PMC7203781 OR  PMC7206980 OR  PMC7214627 OR  PMC7214803 OR  PMC7220991
    )
    INFO: Total Hits are 20
    WARNING: Could not find more papers
    1it [00:00, 505.46it/s]
    100%|█████████████████████████████████████████████| 20/20 [00:32<00:00,  1.61s/it]

9.1.11. 9.1.11 Log levels
~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify the log level using the ``-l`` flag. The default as
you've already seen so far is info.

INPUT:

::

    pygetpapers -q "lantana" -k 10 -o lantana_test_10_2 --loglevel debug -x

9.1.12. Log file
~~~~~~~~~~~~~~~~

You can also choose to write the log to a ``.txt`` file while
simultaneously printing it out.

INPUT:

::

    pygetpapers -q "lantana" -k 10 -o lantana_test_10_4 --loglevel debug -x --logfile test_log.txt

9.2. Crossref
-------------

You can query crossref api only for the metadata. ### 9.2.1. Sample
query - The metadata formats flags are applicable as described in the
EPMC tutorial - ``--terms`` and ``-q`` are also applicable to crossref
INPUT:

::

    pygetpapers --api crossref -q "essential oil" --terms C:\Users\shweata\essential_oil_terms.txt -k 10 -o "terms_test_essential_oil_crossref_3" -x -c --makehtml

OUTPUT:

::

    INFO: Final query is (essential oil AND (antioxidant OR  antibacterial OR  antifungal OR  antiseptic OR  antitrichomonal agent))
    INFO: Making request to crossref
    INFO: Got request result from crossref
    INFO: Making csv files for metadata at C:\Users\shweata\terms_test_essential_oil_crossref_3
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 185.52it/s]
    INFO: Making html files for metadata at C:\Users\shweata\terms_test_essential_oil_crossref_3
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 87.98it/s]
    INFO: Making xml files for metadata at C:\Users\shweata\terms_test_essential_oil_crossref_3
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 366.97it/s]
    INFO: Wrote metadata file for the query
    INFO: Writing metadata file for the papers at C:\Users\shweata\terms_test_essential_oil_crossref_3
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 996.82it/s]

9.2.2. Filter
~~~~~~~~~~~~~

9.3. arxiv
----------

``pygetpapers`` allows you to query ``arxiv`` wrapper for metadata and
get results in XML format. ### 9.3.1. Sample query INPUT

::

    pygetpapers --api arxiv -k 10 -o arxiv_test_2 -q "artificial intelligence" -x

OUTPUT

::


    INFO: Final query is artificial intelligence
    INFO: Making request to Arxiv through pygetpapers
    INFO: Got request result from Arxiv through pygetpapers
    INFO: Requesting 10 results at offset 0
    INFO: Requesting page of results
    INFO: Got first page; 10 of 10 results available
    INFO: Making xml files for metadata at C:\Users\shweata\arxiv_test_2
    100%|█████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 427.09it/s]
    100%|█████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 982.89it/s]

9.4. Biorxiv and Medrxiv
------------------------

You can query ``biorxiv`` and ``medrxiv`` for fulltext and metadata (in
all available formats) ### 9.4.1. Sample Query INPUT:

::

    pygetpapers --api biorxiv --startdate 2021-04-01 -o biorxiv_test -x -c --makehtml  -k 20

OUTPUT:

::

    INFO: Final query is (Default Pygetpapers Query) AND (FIRST_PDATE:[2021-04-01 TO 2021-07-19])
    INFO: Making Request to rxiv
    INFO: Making csv files for metadata at C:\Users\shweata\biorxiv_test
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 17/17 [00:00<00:00, 253.38it/s]
    INFO: Making html files for metadata at C:\Users\shweata\biorxiv_test
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 17/17 [00:00<00:00, 218.29it/s]
    INFO: Making xml for paper
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 17/17 [00:33<00:00,  1.99s/it]
    INFO: Wrote metadata file for the query
    INFO: Writing metadata file for the papers at C:\Users\shweata\biorxiv_test
    100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 17/17 [00:00<00:00, 1369.32it/s]

9.4.2. ``--update``
~~~~~~~~~~~~~~~~~~~

Ensure that you specify the ``--api`` you used to download the existing
corpus while updating. INPUT:

::

    pygetpapers --api biorxiv --update C:\Users\shweata\biorxiv_test_4\rxiv-results.json -k 10 --startdate 2021-07-03

OUTPUT:

::

    INFO: Final query is (False) AND (FIRST_PDATE:[2021-07-03 TO 2021-07-21])
    INFO: Reading old json metadata file
    INFO: Making Request to rxiv
    INFO: Wrote metadata file for the query
    INFO: Writing metadata file for the papers at C:\Users\shweata

9.5.1. Sample Query
~~~~~~~~~~~~~~~~~~~

INPUT

::

    pygetpapers --api medrxiv --startdate 2021-04-01 -o medrxiv_test_2 -x -c -p  --makehtml -k 20

OUTPUT

::

    INFO: Final query is (Default Pygetpapers Query) AND (FIRST_PDATE:[2021-04-01 TO 2021-07-19])
    INFO: Making Request to rxiv
    INFO: Making csv files for metadata at C:\Users\shweata\medrxiv_test_2
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:00<00:00, 168.70it/s]
    INFO: Making html files for metadata at C:\Users\shweata\medrxiv_test_2
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:00<00:00, 229.12it/s]
    INFO: Making xml for paper
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:38<00:00,  1.92s/it]
    INFO: Wrote metadata file for the query
    INFO: Writing metadata file for the papers at C:\Users\shweata\medrxiv_test_2
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:00<00:00, 241.71it/s]

-  ``--update`` would work the same as medarxiv ## 9.6. rxivist
-  Queries both ``biorxiv`` and ``medarxiv``. The difference here is
   that you can specify a query. But rxivist has now clubbed ``biorxiv``
   and ``medarxiv``. That would mean that your downloads would be a
   mixture of both.

You can only retrieve metadata from ``rxivist``.

INPUT:

::

    pygetpapers --api rxivist -q "biomedicine" -k 10 -c -x -o "biomedicine_rxivist" --makehtml -p

OUTPUT:

::

    WARNING: Pdf is not supported for this api
    INFO: Final query is biomedicine
    INFO: Making Request to rxivist
    INFO: Making csv files for metadata at C:\Users\shweata\biomedicine_rxivist
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 125.54it/s]
    INFO: Making html files for metadata at C:\Users\shweata\biomedicine_rxivist
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 124.71it/s]
    INFO: Making xml files for metadata at C:\Users\shweata\biomedicine_rxivist
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 633.38it/s]
    INFO: Wrote metadata file for the query
    INFO: Writing metadata file for the papers at C:\Users\shweata\biomedicine_rxivist
    100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 751.09it/s]

10. Contributions
=================

Contributions are welcome through issues as well as pull requests. For
direct contributions, you can mail the author at ayush@science.org.in.

To discuss problems or feature requests, file an issue. For bugs, please
include as much information as possible, including operating system,
python version, and version of all dependencies.

To contribute, make a pull request. Contributions should include tests
for any new features/bug fixes and follow best practices including PEP8,
etc.

11. Feature Requests
====================

To request features, please put them in issues

12. Legal Implications
======================

If you use\ ``pygetpapers``, you should be careful to understand the law
as it applies to their content mining, as they assume full
responsibility for their actions when using the software.

12.1. Countries with copyright exceptions for content mining:
-------------------------------------------------------------

-  UK
-  Japan

12.2. Countries with proposed copyright exceptions:
---------------------------------------------------

-  Ireland
-  EU countries

12.3. Countries with permissive interpretations of 'fair use' that might allow content mining:
----------------------------------------------------------------------------------------------

-  Israel
-  USA
-  Canada

12.4. General summaries and guides:
-----------------------------------

-  *"The legal framework of text and data mining (TDM)"*, carried out
   for the European Commission in March 2014
   (`PDF <http://ec.europa.eu/internal_market/copyright/docs/studies/1403_study2_en.pdf>`__)
-  *"Standardisation in the area of innovation and technological
   development, notably in the field of Text and Data Mining"*, carried
   out for the European Commission in 2014
   (`PDF <http://ec.europa.eu/research/innovation-union/pdf/TDM-report_from_the_expert_group-042014.pdf>`__)

