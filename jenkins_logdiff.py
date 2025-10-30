import sys
import re
import tempfile
import subprocess
import os
import time

def strip_log_prefix(line):
    """Removes common log prefixes like timestamps."""
    # This regex removes a timestamp like '13:46:53 ' and potential pipeline tags
    return re.sub(r'^\d{2}:\d{2}:\d{2}\s*(\[Pipeline\]\s*)?', '', line)

def main():
    """
    Compares two log files by stripping prefixes and opening the result
    in VS Code's diff view.
    """
    if len(sys.argv) != 3:
        print("Usage: python log_diff.py <file1> <file2>", file=sys.stderr)
        sys.exit(1)

    file1_path = sys.argv[1]
    file2_path = sys.argv[2]

    try:
        with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
            # Create content with prefixes stripped for comparison
            stripped_content1 = "".join([strip_log_prefix(line) for line in f1])
            stripped_content2 = "".join([strip_log_prefix(line) for line in f2])
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create two named temporary files that won't be deleted immediately
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f"_{os.path.basename(file1_path)}") as temp1, \
         tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f"_{os.path.basename(file2_path)}") as temp2:
        
        temp1.write(stripped_content1)
        temp2.write(stripped_content2)
        
        temp1_path = temp1.name
        temp2_path = temp2.name

    print("Generated temporary files for comparison.")
    print("Opening diff in Visual Studio Code...")

    try:
        # Launch VS Code's diff tool
        subprocess.run(['code', '--diff', temp1_path, temp2_path], check=True)
        
        # Give user time to see the diff before cleaning up
        print("VS Code has been launched. The temporary files will be deleted after you close the diff.")
        # A simple wait loop until one of the files is no longer accessible
        # This is a proxy for the user closing the diff tab in VS Code
        while os.path.exists(temp1_path) and os.path.exists(temp2_path):
             time.sleep(5) # Check every 5 seconds

    except FileNotFoundError:
        print("\nError: The 'code' command was not found.", file=sys.stderr)
        print("Please ensure VS Code is installed and the 'code' command is in your system's PATH.", file=sys.stderr)
        print(f"Your temporary files have been saved at:\n- {temp1_path}\n- {temp2_path}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error launching VS Code: {e}", file=sys.stderr)
    finally:
        # Clean up the temporary files
        if os.path.exists(temp1_path):
            os.remove(temp1_path)
        if os.path.exists(temp2_path):
            os.remove(temp2_path)
        print("Temporary files have been cleaned up.")


if __name__ == "__main__":
    main()
