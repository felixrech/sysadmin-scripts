import sys
from subprocess import run


try:
    p = run("zpool list -o name,health", shell=True, capture_output=True)
    out = p.stdout.decode('utf-8').splitlines()

    # Extract line for fileserver pool
    fileserver = [l for l in out if l.startswith('fileserver-pool')][0]
    # Extract everything but last char (a %-sign) from second column and convert to int
    health = fileserver.split()[1]

    # Return respective state
    if health == 'ONLINE':
        sys.exit(0)   # OK
    else:
        sys.exit(2)   # CRITICAL

# Something, somewhere went wrong -> service status unknown
except Exception:
    sys.exit(3)       # UNKNOWN
