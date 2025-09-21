#!/usr/bin/env python3
"""
Validate people markdown files against schema rules.
This script only validates - it doesn't generate any output files.
"""

import sys

# Import our modules
from common import initialize_script, validate_and_report
from markdown_parser import parse_markdown_file


def main():
    """Main validation function."""
    # Initialize script with people directory and schema requirements
    people_dir, validation_rules, markdown_files = initialize_script()

    print(f"Validating {len(markdown_files)} markdown files...")

    # Validate all files and report results
    success = validate_and_report(markdown_files, validation_rules, parse_markdown_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()