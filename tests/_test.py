import pytest
import os
paper_for_references_test = "PMC8348691"
paper_for_citations_test = "PMC7645447"
category_for_references_test = "AGR"
category_for_citations_test = "AGR"
paper_for_zip = "PMC7645447"
paper_for_supp = "PMC8112658"
current_path = os.path.join(os.getcwd(), "temporary_testing_directory")
eupmc_json_path = os.path.join(current_path, "eupmc_results.json")
crossref_json_path = os.path.join(current_path, "crossref_results.json")
arxiv_json_path = os.path.join(current_path, "arxiv_results.json")
rxiv_json_path = os.path.join(current_path, "rxiv_results.json")
citation_path = os.path.join(
    current_path, paper_for_citations_test, "citation.xml")
references_path = os.path.join(
    current_path, paper_for_citations_test, "citation.xml")
path_for_zip = os.path.join(current_path, paper_for_zip, 'ftpfiles')
path_for_supp = os.path.join(
    current_path, paper_for_supp, "supplementaryfiles")
logfile_name = "abc.txt"
path_for_logfile = os.path.join(current_path, logfile_name)

os.system(f'pygetpapers -q "lantana" -k 5 -o "{current_path}"')


def test_directory_creation():
    print("Checking if directory exists")
    does_directory_exist = os.path.exists(current_path)
    assert does_directory_exist == True


def test_does_europepmc_json_file_exists():
    print("Checking if query run successfully")
    does_europepmc_json_file_exist = os.path.isfile(eupmc_json_path)
    assert does_europepmc_json_file_exist == True


def test_eupmc_does_update_work():
    print("Checking Update")
    path, dirs, files = next(os.walk(current_path))
    old_file_count = len(dirs)
    os.system(f'pygetpapers -q "lantana" -k 5 --update -o {current_path}')
    path, dirs, files = next(os.walk(current_path))
    new_file_count = len(dirs)
    print(new_file_count)
    assert (old_file_count+5) == new_file_count


def test_does_zip_work():
    print("checking zip")
    os.system(f'pygetpapers -q {paper_for_zip} -o {current_path} -k 1 --zip')
    does_zip_folder_exist = os.path.isdir(path_for_zip)
    assert does_zip_folder_exist


def test_does_supplementary_work():
    print("checking supp")
    os.system(f'pygetpapers -q {paper_for_supp} -o {current_path} -k 1 --supp')
    does_supp_folder_exist = os.path.isdir(path_for_supp)
    assert does_supp_folder_exist


def does_references_work():
    print("Checking references")
    os.system(
        f'pygetpapers -q {paper_for_references_test} -o {current_path} -k 1 --supp')
    does_references_exist = os.path.isfile(references_path)
    assert does_references_exist


def does_citations_work():
    print("Checking citations")
    os.system(
        f'pygetpapers -q {paper_for_citations_test} -o {current_path} -k 1 --supp')
    does_citations_exist = os.path.isfile(citation_path)
    assert does_citations_exist


def test_does_crossref_work():
    os.system(
        f'pygetpapers -q "lantana" -k 5 -o "{current_path}" --api "crossref" ')
    print("Checking if query run successfully")
    does_crossref_json_file_exist = os.path.isfile(crossref_json_path)
    assert does_crossref_json_file_exist == True


def test_does_arxiv_work():
    os.system(
        f'pygetpapers -q "lantana" -k 5 -o "{current_path}" --api "arxiv" ')
    print("Checking if query run successfully")
    exists_arxiv_json_path = os.path.isfile(arxiv_json_path)
    assert exists_arxiv_json_path == True


def test_does_logfile_work():
    os.system(
        f'pygetpapers -q lantana -o "{current_path}" -k 1 --logfile {logfile_name}')
    does_logfile_exist = os.path.isfile(path_for_logfile)
    assert does_logfile_exist


def test_does_biorxiv_work():
    os.system(
        f'pygetpapers -k 5 -o "{current_path}" --api "biorxiv" ')
    print("Checking if query run successfully")
    exists_rxiv_json_path = os.path.isfile(rxiv_json_path)
    assert exists_rxiv_json_path == True


def test_remove_dir():
    import shutil
    shutil.rmtree(current_path)
    assert "Ran all the tests" == "Ran all the tests"
