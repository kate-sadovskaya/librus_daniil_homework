import subprocess
import sys
import time
from datetime import datetime

RUN_HOURS = {8, 10, 12, 14, 16, 18, 20}
POLL_SECONDS = 30


def main() -> None:
    print(f"Scheduler started. Will run main.py at hours: {sorted(RUN_HOURS)}", flush=True)
    last_run_key = None
    while True:
        now = datetime.now()
        key = (now.date(), now.hour)
        if now.hour in RUN_HOURS and now.minute == 0 and key != last_run_key:
            print(f"[{now.isoformat()}] Running main.py", flush=True)
            result = subprocess.run([sys.executable, "main.py"])
            print(f"[{datetime.now().isoformat()}] main.py exited with code {result.returncode}", flush=True)
            last_run_key = key
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
