#!/usr/bin/env python3.7

import sys
from subprocess import run


try:
    p = run("zpool list -o name,cap", shell=True, capture_output=True)
    out = p.stdout.decode('utf-8').splitlines()

    # Extract line for fileserver pool
    fileserver = [l for l in out if l.startswith('fileserver-pool')][0]
    # Extract everything but last char (a %-sign) from second column and convert to int
    cap = int(fileserver.split()[1][:-1])

    # Return respective state
    if cap < 80:
        sys.exit(0)   # OK
    elif cap < 90:
        sys.exit(1)   # WARNING
    else:
        sys.exit(2)   # CRITICAL

# Something, somewhere went wrong -> service status unknown
except Exception:
    sys.exit(3)       # UNKNOWN
