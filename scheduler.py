import os
import time

from main import main


def run_scheduler() -> None:
    interval_seconds = int(os.getenv("RUN_INTERVAL_SECONDS", "86400"))
    while True:
        print(f"\n[Scheduler] Starting run at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            main()
        except Exception as exc:
            print(f"[Scheduler] Error during run: {exc}")
        print(f"[Scheduler] Run complete, sleeping for {interval_seconds} seconds")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_scheduler()
