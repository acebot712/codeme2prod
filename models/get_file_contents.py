import os
import subprocess
import logging

class PythonFileReader:
    def __init__(self, path="./"):
        self.path = path
        self.logger = logging.getLogger(__name__)

    def get_files_content(self):
        contents = []
        try:
            for file in os.listdir(self.path):
                if file.endswith('.py'):
                    with open(os.path.join(self.path, file), 'r') as f:
                        contents.append(f"# {file}\n{f.read()}")
        except Exception as e:
            self.logger.error(f'Error occurred while reading the files. Reason: {e}')
        return contents
    
    def get_git_tracked_files_content(self):
        contents = []
        try:
            result = subprocess.check_output(['git', 'ls-files'], cwd=self.path).decode()
            files = result.split('\n')

            for file in files:
                if file.endswith('.py'):
                    full_file_path = os.path.join(self.path, file)
                    with open(full_file_path, 'r') as f:
                        contents.append(f"# {full_file_path}\n{f.read()}")
        except Exception as e:
            self.logger.error(f'Error occurred while reading the git tracked files. Reason: {e}')
        return contents
    
def main():
    # Set logging level to INFO for better visibility
    logging.basicConfig(level=logging.INFO)

    # Create an instance of the PythonFileReader
    reader = PythonFileReader("./")

    # Get contents of .py files in current directory
    # contents = reader.get_files_content()
    # print("\n=== Local Python Files ===\n", "\n\n".join(contents))

    # Get contents of git tracked files in current directory
    tracked_contents = reader.get_git_tracked_files_content()
    print("\n=== Git Tracked Files ===\n", "\n\n".join(tracked_contents))

if __name__ == "__main__":
    main()
