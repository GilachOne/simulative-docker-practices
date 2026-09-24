import argparse
import os
import signal
import time

parser = argparse.ArgumentParser()
parser.add_argument('--name', default=os.getenv('APP_NAME', 'student'))
parser.add_argument('--wait', action='store_true')
args = parser.parse_args()
print(f"Hello, {args.name}! Version: {os.getenv('APP_VERSION', 'unknown')}", flush=True)
if args.wait:
    signal.signal(signal.SIGTERM, lambda *_: exit(0))
    while True:
        time.sleep(1)
