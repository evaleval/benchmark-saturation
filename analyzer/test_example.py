#!/usr/bin/env python3
"""
Test script to run the metrics architecture example.
"""

import sys
import os

# Add the src directory to the path so we can import the metrics module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from metrics.examples import run_example

if __name__ == "__main__":
    run_example() 