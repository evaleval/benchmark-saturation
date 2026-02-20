#!/usr/bin/env python3
"""
Test script to run the metrics architecture example.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path so we can import from the analyzer package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analyzer.src.metrics.examples import run_example

if __name__ == "__main__":
    run_example()
