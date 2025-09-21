#!/usr/bin/env python3
"""
Validation module for validating parsed data against schema rules.
"""

from pathlib import Path
from typing import Dict, Any, List


def validate_person_data(data: Dict[str, Any], filepath: Path, validation_rules: Dict[str, Any]) -> List[str]:
    """Validate person data using dynamic rules from template."""
    errors = []
    filename = filepath.name

    # Validate schema version
    if not data.get("schemaVersion"):
        errors.append(f"{filename}: Missing schema version")
    elif data["schemaVersion"] != validation_rules["schema_version"]:
        errors.append(f"{filename}: Invalid schema version '{data['schemaVersion']}', expected '{validation_rules['schema_version']}'")

    # Validate preferred name
    preferred_name_rule = validation_rules["preferred_name"]
    if preferred_name_rule["required"]:
        if not data.get("preferredName"):
            errors.append(f"{filename}: Missing preferred name (# heading)")
        elif not data["preferredName"].strip():
            errors.append(f"{filename}: Preferred name is empty")

    # Validate image
    image_rule = validation_rules["image"]
    if image_rule["required"]:
        if not data.get("image"):
            errors.append(f"{filename}: Missing image reference")

    # Validate info section fields
    info = data.get("info", {})
    for field_name, rule in validation_rules["info_fields"].items():
        if rule["required"]:
            if field_name not in info:
                errors.append(f"{filename}: Missing required info field '{field_name}'")
            elif field_name == "tags":
                if not isinstance(info[field_name], list) or len(info[field_name]) == 0:
                    errors.append(f"{filename}: Tags must be a non-empty array")
                elif any(not tag.strip() for tag in info[field_name]):
                    errors.append(f"{filename}: Tags cannot be empty strings")
                elif "min_items" in rule and len(info[field_name]) < rule["min_items"]:
                    errors.append(f"{filename}: Tags must have at least {rule['min_items']} item(s)")
            elif not info[field_name] or not str(info[field_name]).strip():
                errors.append(f"{filename}: Info field '{field_name}' cannot be empty")

    # Validate sections
    for section_name, rule in validation_rules["sections"].items():
        section_data = data.get(section_name, [])

        if rule["required"]:
            if rule["type"] == "array":
                if not isinstance(section_data, list) or len(section_data) == 0:
                    section_display = section_name.replace("knownFor", "Known For").replace("impact", "Impact")
                    errors.append(f"{filename}: '{section_display}' section must have at least one item")
                elif any(not item.strip() for item in section_data):
                    section_display = section_name.replace("knownFor", "Known For").replace("impact", "Impact")
                    errors.append(f"{filename}: '{section_display}' items cannot be empty")
                elif "min_items" in rule and len(section_data) < rule["min_items"]:
                    section_display = section_name.replace("knownFor", "Known For").replace("impact", "Impact")
                    errors.append(f"{filename}: '{section_display}' section must have at least {rule['min_items']} item(s)")

            elif rule["type"] == "link":
                if not isinstance(section_data, list) or len(section_data) == 0:
                    errors.append(f"{filename}: 'Sources' section must have at least one item")
                elif "min_items" in rule and len(section_data) < rule["min_items"]:
                    errors.append(f"{filename}: 'Sources' section must have at least {rule['min_items']} item(s)")
                else:
                    for i, source in enumerate(section_data):
                        if not isinstance(source, dict):
                            errors.append(f"{filename}: Source {i+1} is not properly formatted")
                            continue
                        if not source.get("description") or not source["description"].strip():
                            errors.append(f"{filename}: Source {i+1} missing description")
                        if not source.get("url") or not source["url"].strip():
                            errors.append(f"{filename}: Source {i+1} missing URL")

    return errors


def validate_files(file_paths: List[Path], validation_rules: Dict[str, Any], parse_func) -> List[str]:
    """Validate multiple files and return all errors."""
    all_errors = []

    for file_path in file_paths:
        try:
            data = parse_func(file_path)
            errors = validate_person_data(data, file_path, validation_rules)
            all_errors.extend(errors)
        except Exception as e:
            error_msg = f"{file_path.name}: Parsing error - {str(e)}"
            all_errors.append(error_msg)

    return all_errors


def print_validation_results(errors: List[str], total_files: int) -> bool:
    """Print validation results and return True if all passed."""
    if errors:
        print(f"\nVALIDATION FAILED: Found {len(errors)} error(s)")
        print("\nAll validation errors:")
        for error in errors:
            print(f"  ERROR: {error}")
        print(f"\nPlease fix the above errors and try again.")
        return False
    else:
        print(f"\nVALIDATION PASSED: All {total_files} files are valid")
        return True