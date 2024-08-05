"""
Script to update the docs index.rst file automatically.
* Removes the deleted sub-packages from the toctree directive (if any).
* Adds the new sub-packages to the toctree directive (if any).
"""

from pathlib import Path

main_dir_name = "soupsavvy"
# The package directory to search for new sub-packages
soupsavvy_dir = Path(main_dir_name)

# The docs main index file to be updated
index_file = Path("docs", "source", "index.md")


def main():
    with index_file.open() as f:
        contents = f.readlines()

    index_packages = [line.strip() for line in contents if f"{main_dir_name}." in line]

    # Get the list of current sub-packages (only if directory has __init__.py file)
    current_folders = {
        f"{main_dir_name}.{f.name}"
        for f in soupsavvy_dir.iterdir()
        if f.is_dir() and Path(f, "__init__.py").exists()
    }

    # check for changes
    new_folders = current_folders - set(index_packages)
    deleted_folders = set(index_packages) - current_folders

    if new_folders:
        print(f"New sub-packages detected: {new_folders}")

        # Find the line with the toctree directive
        for i, line in enumerate(contents):
            if index_packages[-1] in line:
                break
        else:
            raise ValueError("Could not find toctree directive in index.rst")

        # Add the new folders to the toctree
        for folder in new_folders:
            contents.insert(i + 1, f"{folder}\n")

    if deleted_folders:
        print(f"Deleted sub-packages detected: {deleted_folders}")
        # Remove the deleted folders from the toctree
        contents = [line for line in contents if line.strip() not in deleted_folders]

    if deleted_folders or new_folders:
        # Write the updated contents back to the file
        with index_file.open("w") as f:
            f.writelines(contents)

        print(f"{index_file} file updated successfully.")
    else:
        print("No changes detected.")


if __name__ == "__main__":
    main()
