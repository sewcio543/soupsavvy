"""
Script to update the docs index.rst file automatically.
- Removes deleted demos from the toctree directive (if any).
- Adds new demos the toctree directive (if any).
"""

from pathlib import Path

# The directory to search for new demos
demos_dir = Path("docs", "source", "demos")

# The docs main index file to be updated
index_file = Path("docs", "source", "index.md")


def main() -> None:
    """
    Updates content of index.rst with project demos.
    Keeps index.rst in sync with the demos directory.
    """
    with index_file.open() as f:
        contents = f.readlines()

    demos = [line.strip() for line in contents if "demos/" in line]

    # Get the list of current demos (.ipynb files in demos directory)
    current = {
        f"demos/{f.name}"[:-6]
        for f in demos_dir.iterdir()
        if Path(f).suffix == ".ipynb"
    }

    # check for changes
    new = current - set(demos)
    deleted = set(demos) - current

    if new:
        print(f"New demos detected: {new}")

        # Find the line with the toctree directive
        for i, line in enumerate(contents):
            if demos[-1] in line:
                break
        else:
            raise ValueError("Could not find toctree directive in index.rst")

        # Add the new folders to the toctree
        for demo in new:
            contents.insert(i + 1, f"{demo}\n")

    if deleted:
        print(f"Deleted demos detected: {deleted}")
        # Remove the deleted folders from the toctree
        contents = [line for line in contents if line.strip() not in deleted]

    if deleted or new:
        # Write the updated contents back to the file
        with index_file.open("w") as f:
            f.writelines(contents)

        print(f"{index_file} file updated successfully.")
    else:
        print("No changes detected.")


if __name__ == "__main__":
    main()
