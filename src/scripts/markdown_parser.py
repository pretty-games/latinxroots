#!/usr/bin/env python3
"""
Markdown parsing module for extracting structured data from markdown files.
"""

import re
from pathlib import Path
from typing import Dict, Any


def parse_markdown_file(filepath: Path) -> Dict[str, Any]:
    """Parse markdown file into structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # Extract schema version
    schema_version = None
    if lines[0].startswith('**schema-version:**'):
        schema_version = lines[0].split('**schema-version:**')[1].strip()

    # Extract preferred name (first # heading)
    preferred_name = None
    for line in lines:
        if line.startswith('# '):
            preferred_name = line[2:].strip()
            break

    # Extract image path and update to people/images
    image_path = None
    image_match = re.search(r'!\[.*?\]\((.*?)\)', content)
    if image_match:
        original_path = image_match.group(1)
        # Convert images/filename to people/images/filename
        if original_path.startswith('images/'):
            image_path = f"people/{original_path}"
        else:
            image_path = original_path

    # Parse Info section
    info = {}
    in_info_section = False

    for line in lines:
        if line.strip() == '## Info':
            in_info_section = True
            continue
        elif line.startswith('## ') and in_info_section:
            break
        elif in_info_section and line.strip().startswith('- **'):
            # Parse info items like "- **Full Name:** value"
            match = re.match(r'- \*\*(.*?):\*\* (.*)', line.strip())
            if match:
                key = match.group(1).lower().replace(' ', '')
                value = match.group(2)

                # Special handling for tags
                if key == 'tags':
                    # Extract array from [value, value, value] format
                    tags_match = re.search(r'\[(.*?)\]', value)
                    if tags_match:
                        tags_str = tags_match.group(1)
                        tags = [tag.strip() for tag in tags_str.split(',')]
                        info[key] = tags
                    else:
                        info[key] = []
                else:
                    info[key] = value

    # Parse Known For section
    known_for = []
    in_known_for = False

    for line in lines:
        if line.strip() == '## Known For':
            in_known_for = True
            continue
        elif line.startswith('## ') and in_known_for:
            break
        elif in_known_for and line.strip().startswith('- '):
            known_for.append(line.strip()[2:])

    # Parse Impact section
    impact = []
    in_impact = False

    for line in lines:
        if line.strip() == '## Impact (to society and latino community)':
            in_impact = True
            continue
        elif line.startswith('## ') and in_impact:
            break
        elif in_impact and line.strip().startswith('- '):
            impact.append(line.strip()[2:])

    # Parse Sources section
    sources = []
    in_sources = False

    for line in lines:
        if line.strip() == '## Sources':
            in_sources = True
            continue
        elif line.startswith('## ') and in_sources:
            break
        elif in_sources and line.strip().startswith('- '):
            # Parse markdown links like "- [description](url)"
            source_text = line.strip()[2:]
            link_match = re.match(r'\[(.*?)\]\((.*?)\)', source_text)
            if link_match:
                sources.append({
                    "description": link_match.group(1),
                    "url": link_match.group(2)
                })
            else:
                # If not a link, treat as plain text
                sources.append({
                    "description": source_text,
                    "url": ""
                })

    return {
        "schemaVersion": schema_version,
        "preferredName": preferred_name,
        "image": image_path,
        "info": info,
        "knownFor": known_for,
        "impact": impact,
        "sources": sources
    }


def get_markdown_files(directory: Path, exclude_patterns: list = None) -> list[Path]:
    """Get all markdown files in a directory, excluding specified patterns."""
    if exclude_patterns is None:
        exclude_patterns = ["_*"]  # Default: exclude files starting with underscore

    markdown_files = []
    for md_file in directory.glob("*.md"):
        excluded = False
        for pattern in exclude_patterns:
            if md_file.name.startswith(pattern.replace("*", "")):
                excluded = True
                break
        if not excluded:
            markdown_files.append(md_file)

    return sorted(markdown_files)