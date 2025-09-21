#!/usr/bin/env python3
"""
Schema parsing module for extracting validation rules from template files.
"""

import re
from pathlib import Path
from typing import Dict, Any


def parse_template_validation_rules(template_path: Path) -> Dict[str, Any]:
    """Parse validation rules from template file."""
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    validation_rules = {
        "schema_version": "1.0",
        "preferred_name": {"required": True, "type": "string"},
        "image": {"required": True, "type": "image"},
        "info_fields": {},
        "sections": {}
    }

    # Extract schema version requirement
    if lines and lines[0].startswith('**schema-version:**'):
        validation_rules["schema_version"] = lines[0].split('**schema-version:**')[1].strip()

    # Parse placeholders using regex
    placeholder_pattern = r'\{([^}]+)\}'

    # Parse preferred name (first # heading)
    for line in lines:
        if line.startswith('# '):
            match = re.search(placeholder_pattern, line)
            if match:
                placeholder = match.group(1)
                parts = placeholder.split(':')
                validation_rules["preferred_name"] = {
                    "required": parts[0] == "required",
                    "type": parts[1] if len(parts) > 1 else "string"
                }
            break

    # Parse image requirement
    for line in lines:
        if line.strip().startswith('!['):
            validation_rules["image"] = {"required": True, "type": "image"}
            break

    # Parse Info section fields
    in_info_section = False
    for line in lines:
        if line.strip() == '## Info':
            in_info_section = True
            continue
        elif line.startswith('## ') and in_info_section:
            break
        elif in_info_section and line.strip().startswith('- **'):
            # Parse info items like "- **Full Name:** {required:string}" or "- **Tags:** [{required:array:min:1}]"
            match = re.match(r'- \*\*(.*?):\*\* (.+)', line.strip())
            if match:
                field_name = match.group(1).lower().replace(' ', '')
                value_part = match.group(2)

                # Look for placeholder in the value part (could be inside brackets)
                placeholder_match = re.search(r'\{([^}]+)\}', value_part)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    parts = placeholder.split(':')

                    rule = {
                        "required": parts[0] == "required",
                        "type": parts[1] if len(parts) > 1 else "string"
                    }

                    # Handle array with minimum requirements
                    if len(parts) > 2 and parts[2] == "min":
                        rule["min_items"] = int(parts[3]) if len(parts) > 3 else 1

                    validation_rules["info_fields"][field_name] = rule

    # Parse section requirements
    current_section = None
    for line in lines:
        if line.startswith('## '):
            section_name = line[3:].strip()
            if section_name == "Known For":
                current_section = "knownFor"
            elif section_name == "Impact (to society and latino community)":
                current_section = "impact"
            elif section_name == "Sources":
                current_section = "sources"
            else:
                current_section = None
        elif current_section and line.strip().startswith('- '):
            # Parse placeholder in list item
            match = re.search(placeholder_pattern, line)
            if match:
                placeholder = match.group(1)
                parts = placeholder.split(':')

                rule = {
                    "required": parts[0] == "required",
                    "type": parts[1] if len(parts) > 1 else "string"
                }

                # Handle array/link with minimum requirements
                if len(parts) > 2 and parts[2] == "min":
                    rule["min_items"] = int(parts[3]) if len(parts) > 3 else 1

                validation_rules["sections"][current_section] = rule
                # Move to next section after capturing rule

    return validation_rules


def get_schema_path(object_type: str, version: str) -> Path:
    """Get the path to a schema file."""
    return Path("schema") / f"{object_type}_{version}.md"


def load_people_schema(version: str = "1.0") -> Dict[str, Any]:
    """Load the people schema for a specific version."""
    schema_path = get_schema_path("PEOPLE", version)
    return parse_template_validation_rules(schema_path)