#!/usr/bin/env python3
"""
Test script to run the metrics architecture example.
"""

import sys
import os

# Add the analyzer directory to the path so we can import from the analyzer package
sys.path.insert(0, '/Users/random/benchmark-saturation')

from analyzer.src.metrics.examples import run_example

if __name__ == "__main__":
    run_example() 