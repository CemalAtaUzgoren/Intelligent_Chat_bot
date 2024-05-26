import os
import subprocess
import multiprocessing


class ScrapersRunner(object):
    def __init__(self):
        self.get_py_files_dir = os.getcwd()

    def find_scraper_files(self):
        # Get Scraper py files and store them in a list
        scraper_files_list = []
        for file in os.listdir(self.get_py_files_dir):
            if file.endswith("_scraper.py"):
                scraper_files_list.append(file)
        return scraper_files_list

    def execute_python_file(self, file_name):
        process = subprocess.run(["python", file_name], capture_output=True, text=True)
        return process.returncode == 0  # Returns True if the process exited successfully

    def main(self):
        # Get Python files
        python_files = self.find_scraper_files()

        # Creating a multiprocessing pool
        pool = multiprocessing.Pool()

        # Trigger the execution of each file in parallel
        results = pool.map(self.execute_python_file, python_files)

        # Close multiprocessing pool
        pool.close()
        pool.join()

        # Check if all subprocesses were successful
        all_successful = all(results)
        return all_successful  


if __name__ == "__main__":
    obj = ScrapersRunner()
    obj.main()