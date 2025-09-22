#!/usr/bin/env python3
"""
Common utilities and initialization functions for scripts.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

from schema_parser import load_people_schema
from markdown_parser import get_markdown_files


def initialize_script(require_people_dir: bool = True, require_schema: bool = True) -> tuple[Path, Dict[str, Any], List[Path]]:
    """Initialize common script requirements."""
    people_dir = Path("src/people")
    validation_rules = None
    markdown_files = []

    if require_people_dir:
        if not people_dir.exists():
            print(f"ERROR: People directory '{people_dir}' not found")
            sys.exit(1)

        markdown_files = get_markdown_files(people_dir)
        if not markdown_files:
            print(f"No markdown files found in {people_dir}")
            if require_schema:
                sys.exit(0)

    if require_schema:
        try:
            validation_rules = load_people_schema("1.0")
            print(f"Loaded validation rules from src/schema/PEOPLE_1.0.md")
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to parse schema validation rules: {e}")
            sys.exit(1)

    return people_dir, validation_rules, markdown_files


def validate_and_report(markdown_files: List[Path], validation_rules: Dict[str, Any], parse_func) -> bool:
    """Validate files and report results."""
    from validator import validate_files, print_validation_results

    errors = validate_files(markdown_files, validation_rules, parse_func)
    return print_validation_results(errors, len(markdown_files))


def ensure_output_dir(output_dir: Path) -> Path:
    """Ensure output directory exists and return it."""
    output_dir.mkdir(exist_ok=True)
    return output_dir