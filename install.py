import os
import subprocess
import sys

from settings import venv_dir


def setup_virtual_environment():
    # Check if the virtual environment already exists
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print("Virtual environment already exists.")

    if os.name == "nt":  # Windows
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    # Install dependencies from requirements.txt
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print("Installing dependencies from requirements.txt...")
        try:
            subprocess.run(
                [venv_python, "-m", "pip", "install", "-r", requirements_file],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print(f"{requirements_file} not found. No dependencies to install.")


if __name__ == "__main__":
    setup_virtual_environment()
