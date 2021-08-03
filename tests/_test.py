import pytest
import os
current_path = os.path.join(os.getcwd(), "temporary_testing_directory")
eupmc_json_path = os.path.join(current_path, "eupmc_results.json")
crossref_json_path = os.path.join(current_path, "crossref_results.json")
arxiv_json_path = os.path.join(current_path, "arxiv_results.json")
rxiv_json_path = os.path.join(current_path, "rxiv_results.json")

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
