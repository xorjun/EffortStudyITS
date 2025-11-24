import subprocess

if __name__ == "__main__":
    subprocess.run(["ls && cd its_ui && ng serve"], shell=True)