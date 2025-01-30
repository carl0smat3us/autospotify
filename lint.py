import os
import subprocess


def format_python_files():
    for root, dirs, files in os.walk("."):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    subprocess.run(["isort", file_path], check=True)
                    subprocess.run(["black", file_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    format_python_files()
