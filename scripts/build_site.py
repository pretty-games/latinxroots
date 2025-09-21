#!/usr/bin/env python3
"""
Build static site by generating JSON files and preparing documentation.
This script validates files and generates JSON output for static hosting.
"""

import json
import shutil
import sys
from pathlib import Path

# Import our modules
from common import initialize_script, ensure_output_dir
from markdown_parser import parse_markdown_file
from validator import validate_files


def generate_json_files(markdown_files: list[Path], validation_rules: dict, output_dir: Path) -> tuple[list[str], list[str]]:
    """Generate JSON files from markdown files."""
    people_output_dir = output_dir / "people"
    people_output_dir.mkdir(parents=True, exist_ok=True)

    json_files = []
    all_errors = []

    for md_file in markdown_files:
        print(f"Processing {md_file.name}...")

        try:
            data = parse_markdown_file(md_file)
            validation_errors = validate_files([md_file], validation_rules, parse_markdown_file)
            if validation_errors:
                all_errors.extend(validation_errors)
                print(f"  -> Validation errors found in {md_file.name}")
                for error in validation_errors:
                    print(f"    ERROR: {error}")
                continue

            json_filename = md_file.stem + ".json"
            json_path = people_output_dir / json_filename
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            json_files.append(json_filename)
            print(f"  -> Generated {json_filename}")

        except Exception as e:
            error_msg = f"{md_file.name}: Parsing error - {str(e)}"
            all_errors.append(error_msg)
            print(f"  -> Error processing {md_file.name}: {e}")

    return json_files, all_errors


def copy_images(source_dir: Path, output_dir: Path):
    """Copy images directory to output location."""
    images_src = source_dir / "images"
    images_dst = output_dir / "people" / "images"

    if images_src.exists():
        if images_dst.exists():
            shutil.rmtree(images_dst)
        shutil.copytree(images_src, images_dst)
        print(f"Copied images directory to {images_dst}")
    else:
        print(f"No images directory found at {images_src}")


def generate_list_file(json_files: list[str], output_dir: Path):
    """Generate the list.json file with all available JSON files."""
    list_path = output_dir / "people" / "list.json"
    with open(list_path, 'w', encoding='utf-8') as f:
        json.dump(sorted(json_files), f, indent=2)
    print(f"Generated list.json with {len(json_files)} files")


def main():
    """Main site building function."""
    people_dir, validation_rules, markdown_files = initialize_script()
    output_dir = ensure_output_dir(Path("docs"))
    json_files, all_errors = generate_json_files(markdown_files, validation_rules, output_dir)

    if all_errors:
        print(f"\nVALIDATION FAILED: Found {len(all_errors)} error(s)")
        print("\nAll validation errors:")
        for error in all_errors:
            print(f"  ERROR: {error}")
        print(f"\nPlease fix the above errors and try again.")
        sys.exit(1)

    generate_list_file(json_files, output_dir)
    copy_images(people_dir, output_dir)

    print(f"\nSUCCESS: Generated {len(json_files)} JSON files and list.json in {output_dir}")


if __name__ == "__main__":
    main()