pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

pygetpapers makes it really easy to add support for new repositories.

To add a new repository, clone the repo and cd into the directory pygetpapers. Thereafter, create a new module with the class for the repo. Make sure you edit the config.ini file with the specifications of the new repo. 

Following is an example config

```
[europe_pmc]
posturl=https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST
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

After this, in the repo class, ensure that you can request scientific papers, download them and do post-processing on them. There are multiple functions in the class download_tools which can help you with the same. I suggest looking at previously configured repos for the same. 

It is necessary to have three functions in particular.

1) apipaperdownload
2) noexecute
3) update

Following is an example implementation.
``` 
    def update(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        logging.info("Reading old json metadata file")
        update_path = self.get_metadata_results_file()
        os.chdir(os.path.dirname(update_path))
        update = self.download_tools.readjsondata(update_path)
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=update,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI,
            name_of_file=CROSSREF_RESULTS
        )

    def noexecute(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        filter_dict = args.filter
        result_dict = self.crossref(
            query, size=10, filter_dict=filter_dict
        )
        totalhits = result_dict[NEW_RESULTS][TOTAL_HITS]
        logging.info("Total number of hits for the query are %s", totalhits)

    def apipaperdownload(
        self,
        args
    ):
        """[summary]

        :param args: [description]
        :type args: [type]
        """
        query = args.query
        size = args.limit
        filter_dict = args.filter
        makecsv = args.makecsv
        makexml = args.xml
        makehtml = args.makehtml
        result_dict = self.crossref(
            query,
            size,
            filter_dict=filter_dict,
            update=None,
            makecsv=makecsv,
            makexml=makexml,
            makehtml=makehtml,
        )
        self.download_tools.make_json_files_for_paper(
            result_dict[NEW_RESULTS], updated_dict=result_dict[UPDATED_DICT], key_in_dict=DOI, name_of_file=CROSSREF_RESULTS
        )

```

The class ApiPlugger looks for these functions along with the config file to serve the API on the cli.

