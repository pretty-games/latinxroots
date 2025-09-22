#!/usr/bin/env python3
"""
Pre-deployment validation and build script.
This script runs comprehensive checks before deployment.
"""

import sys
from pathlib import Path

# Import our modules
from common import initialize_script, validate_and_report
from markdown_parser import get_markdown_files, parse_markdown_file


def check_schema_files():
    """Check that required schema files exist."""
    schema_dir = Path("schema")
    if not schema_dir.exists():
        print("ERROR: Schema directory not found")
        return False

    people_schema = schema_dir / "PEOPLE_1.0.md"
    if not people_schema.exists():
        print(f"ERROR: People schema file not found: {people_schema}")
        return False

    print(f"[OK] Schema files found")
    return True


def check_people_directory():
    """Check that people directory exists and has content."""
    people_dir = Path("people")
    if not people_dir.exists():
        print("ERROR: People directory not found")
        return False

    markdown_files = get_markdown_files(people_dir)
    if not markdown_files:
        print("ERROR: No markdown files found in people directory")
        return False

    print(f"[OK] Found {len(markdown_files)} people files")
    return True


def run_validation():
    """Run full validation of all people files."""
    print("\n--- Running Validation ---")

    try:
        people_dir, validation_rules, markdown_files = initialize_script()
        print(f"[OK] Loaded validation rules")
        success = validate_and_report(markdown_files, validation_rules, parse_markdown_file)
        return success
    except SystemExit:
        return False
    except Exception as e:
        print(f"ERROR: Validation failed: {e}")
        return False


def check_output_readiness():
    """Check if docs directory is ready for deployment."""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("WARNING: docs directory doesn't exist yet (will be created during build)")
        return True

    people_dir = docs_dir / "people"
    list_json = people_dir / "list.json"

    if list_json.exists():
        print(f"[OK] Found list.json")
    else:
        print("INFO: list.json will be generated during build")

    if people_dir.exists():
        json_files = list(people_dir.glob("*.json"))
        print(f"[OK] Found {len(json_files)} existing JSON files")
    else:
        print("INFO: people JSON files will be generated during build")

    return True


def main():
    """Main deployment check function."""
    print("=== Pre-Deployment Checks ===\n")

    checks = [
        ("Schema Files", check_schema_files),
        ("People Directory", check_people_directory),
        ("Validation", run_validation),
        ("Output Readiness", check_output_readiness),
    ]

    all_passed = True

    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        if not check_func():
            all_passed = False
            print(f"[FAIL] {check_name} FAILED")
        else:
            print(f"[PASS] {check_name} PASSED")

    print(f"\n=== Summary ===")
    if all_passed:
        print("[PASS] All pre-deployment checks PASSED")
        print("Ready for deployment!")
        sys.exit(0)
    else:
        print("[FAIL] Some pre-deployment checks FAILED")
        print("Please fix the issues above before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()