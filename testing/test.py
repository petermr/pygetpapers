import unittest
import os
os.system("pip install git+git://github.com/petermr/pygetpapers")
os.system('pygetpapers -q "lantana" -k 10 -o "test"')
current_path=os.path.join(os.getcwd(),"test")
json_path=os.path.join(current_path,"eupmc_results.json")

class TestStringMethods(unittest.TestCase):

    def test_directory_creation(self):
        does_directory_exist= os.path.exists(current_path)
        self.assertTrue(does_directory_exist)

    def test_does_europepmc_json_file_exists(self):
        does_europepmc_json_file_exist= os.path.isfile(json_path)
        self.assertTrue(does_europepmc_json_file_exist)

    def test_does_restart_work(self):
        os.system(f'pygetpapers -q "lantana" --restart "{json_path}" --xml')
        path, dirs, files = next(os.walk(current_path))
        all_xmls_exist=True
        for file in dirs:
            does_europepmc_xml_file_exist = os.path.isfile(os.path.join(current_path,file,'fulltext.xml'))
            if not does_europepmc_xml_file_exist:
                all_xmls_exist=False
        self.assertTrue(all_xmls_exist)

    def test_does_update_work(self):
        path, dirs, files = next(os.walk(current_path))
        old_file_count = len(dirs)
        os.system(f'pygetpapers -q "lantana" --update "{json_path}" -k 10')
        path, dirs, files = next(os.walk(current_path))
        new_file_count = len(dirs)
        self.assertEqual(old_file_count+10, new_file_count)

    def test_remove_dir(self):
        import shutil
        current_path = os.path.join(os.getcwd(), "test")
        shutil.rmtree(current_path)
        self.assertTrue("sample","sample")


if __name__ == '__main__':
    unittest.main()

