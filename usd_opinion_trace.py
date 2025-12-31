#!/usr/bin/env python3
"""USD Opinion Trace - Simple script wrapper."""

import sys
import os

# Add src to path so we can import opinion_trace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from opinion_trace.cli import main as cli_main


def main():
    """Main entry point for CLI."""
    return cli_main()


if __name__ == '__main__':
    sys.exit(main())
