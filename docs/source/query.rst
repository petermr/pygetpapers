QueryBuilder
============

pygetpapers builds and runs all queries through a query_builder module (`Pygetpapers.py`) .
There are several reasons:

- each repository may use its own query language and syntax
- there is frequent need to use punctuation (e.g. `(..)`, `".."`, `'..'`) and these may be nested. Punctuation can also interact with command-line syntax
- complex queries (e.g. repeated OR, AND, NOT ) are tedious and error-prone
- many values (especially dates) need converting or standardising
- some options require or forbid other options (e.g. `--xml` requires an `--output` value)
- successful queries can be saved , edited, and rerun
- queries may be rerun at a later date, or request a larger number of downloads.

Users may wish to build queries:

- completely from the commandline (`argparse` Namespace).
- from a saved query (`configparser` configuration file)
- programmatically through an instance of `Pygetpapers`
- mixtures of the above

QueryBuilder contains or creates flags indicating which of the following is to be processed

- query strings to be submitted to the particular repository
- flags controlling the execution (download rate, limits, formats)
- creation of the local repository (`CProject`)
- creation of the per-article subdirectories (`CTree`)
- postprocessing options (e.g. `docanalysis` and `py4ami`, and standard Unix/Python libraries)

