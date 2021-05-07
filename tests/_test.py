import pytest
import os
current_path = os.path.join(os.getcwd(), "temporary_testing_directory")
json_path = os.path.join(current_path, "eupmc_results.json")
os.system(f'pygetpapers -q "lantana" -k 5 -o "{current_path}"')


def test_directory_creation():
    print("Checking if directory exists")
    does_directory_exist = os.path.exists(current_path)
    assert does_directory_exist == True


def test_does_europepmc_json_file_exists():
    print("Checking if query run successfully")
    does_europepmc_json_file_exist = os.path.isfile(json_path)
    assert does_europepmc_json_file_exist == True


def test_does_update_work():
    print("Checking Update")
    path, dirs, files = next(os.walk(current_path))
    old_file_count = len(dirs)
    os.system(f'pygetpapers -q "lantana" -k 5 --update "{json_path}"')
    path, dirs, files = next(os.walk(current_path))
    new_file_count = len(dirs)

    assert (old_file_count+5) == new_file_count


def test_remove_dir():
    import shutil
    shutil.rmtree(current_path)
    assert "Ran all the tests" == "Ran all the tests"
