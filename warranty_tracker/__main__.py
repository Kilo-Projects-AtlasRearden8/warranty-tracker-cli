"""Allow running as `python -m warranty_tracker`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
