import threading
import subprocess

# Using subprocesses
# https://docs.python.org/3/library/subprocess.html
# https://www.datacamp.com/tutorial/python-subprocess


# This is the entry point for each script
def run_scripts(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:  {e}")

scripts = ["buzzer.py", "audio_led.py"]


# Create threads each calling the above function 
threads = []
for script in scripts:
    thread = threading.Thread(target=run_scripts, args=(script,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All scripts have finished running.")