# scripts/setup_env.py
import os
import subprocess
import importlib.metadata
from packaging import version

def check_and_install_requirements():
    """Check and install/upgrade dependencies from requirements.txt if needed."""
    print("Checking dependencies...")
    try:
        # Upgrade pip first
        subprocess.check_call(["python", "-m", "pip", "install", "--upgrade", "pip"])
        
        # Read requirements.txt
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip()]
        
        # Check installed versions
        installed = {dist.metadata['Name'].lower(): dist.version for dist in importlib.metadata.distributions()}
        to_install = []
        
        for req in requirements:
            pkg_name = req.split(">=")[0].strip()
            min_version = req.split(">=")[1] if ">=" in req else None
            current_version = installed.get(pkg_name.lower())
            
            if not current_version:
                to_install.append(req)
            elif min_version and version.parse(current_version) < version.parse(min_version):
                to_install.append(req)
        
        if to_install:
            print(f"Installing/upgrading: {to_install}")
            subprocess.check_call(["pip", "install", "--upgrade"] + to_install)
        else:
            print("All dependencies are up-to-date.")
        
        print("Environment setup complete!")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up environment: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    check_and_install_requirements()