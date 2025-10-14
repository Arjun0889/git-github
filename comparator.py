import sys
import re
from collections import defaultdict

def parse_dependencies(filepath):
    """Parses a groovy dependency file and returns a dictionary."""
    dependencies = {}
    # Regex to capture group, name, and version
    dep_regex = re.compile(r"group:'([^']*)',name:'([^']*)',version:'([^']*)'")
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                match = dep_regex.search(line)
                if match:
                    group, name, version = match.groups()
                    key = f"{group}:{name}"
                    dependencies[key] = (version, line_num) # Store version and line number
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        return None
    return dependencies

def main():
    """Main function to compare dependency versions in files."""
    if len(sys.argv) < 3:
        print("Usage: python compare.py <file1> <file2> [<file3>...]", file=sys.stderr)
        sys.exit(1)

    file_paths = sys.argv[1:]
    deps_data = [parse_dependencies(fp) for fp in file_paths]

    if any(data is None for data in deps_data):
        sys.exit(1)

    all_keys = set()
    for data in deps_data:
        all_keys.update(data.keys())

    print(f"Comparing {len(all_keys)} unique dependencies across {len(file_paths)} files...\n")

    differences_found = 0
    matches_found = 0

    # Find and print differences
    for key in sorted(all_keys):
        details = [data.get(key) for data in deps_data]
        versions = {detail[0] if detail else "---MISSING---" for detail in details}

        if len(versions) > 1:
            if differences_found == 0:
                print("--- DIFFERENCES FOUND ---")
            differences_found += 1
            print(f"\nDifference found for: {key}")
            
            version_groups = defaultdict(list)
            for i, detail in enumerate(details):
                version = detail[0] if detail else "---MISSING---"
                line_num = detail[1] if detail else "N/A"
                version_groups[version].append(f"{file_paths[i]} (line {line_num})")

            for version, files in sorted(version_groups.items()):
                print(f"  - Version '{version}' found in:")
                for file_info in files:
                    print(f"    - {file_info}")
            print("-" * 40)
        else:
            matches_found +=1

    if differences_found > 0:
        print("\n" + "="*40)

    print("--- COMPARISON SUMMARY ---")
    print(f"Dependencies with differences: {differences_found}")
    print(f"Dependencies with consistent versions: {matches_found}")
    print("="*40)


if __name__ == "__main__":
    main()
