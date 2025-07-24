"""App startup for development only.
"""
import pathlib
import subprocess
import atexit
import os
import signal
#from courses.parse_courses import parse_course
#from courses.parse_tasks import parse_all_tasks
from pymongo import MongoClient
from api.config import config


def cleanup_child_processes():
    for process in child_processes:
        try:
            os.kill(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # Process already exited


path = pathlib.Path(__file__).parent.resolve()
backend_start = os.path.join(path, "api/main.py")
frontend_start = os.path.join("start_frontend.py")

if __name__ == "__main__":

    # Store references to the child processes
    child_processes = []

    # Register the cleanup function to be called when the script exits
    atexit.register(cleanup_child_processes)

    #Set backend environment Variables for development.
    backend_env = os.environ.copy()
    backend_env["ITS_ENV"] = "development"



    backend = subprocess.Popen([f"python {backend_start}"], shell=True, env=backend_env)
    child_processes.append(backend)
    frontend = subprocess.Popen(["cd frontend && ls  && python start_frontend.py"], shell=True)
    child_processes.append(frontend)

    backend.wait()
    frontend.wait()
