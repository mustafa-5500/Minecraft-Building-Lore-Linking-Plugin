# Post-Implementation Notes [generate_docs.py](../../Utils/documentation-generator/generate_docs.md)

Usage: 
    python generate_docs.py <source_dir> <docs_output_dir>

# main()

Set up the arguements with `argparse.ArgumentParser`. which we can then parsed using `parse_args()`, using the variable names set to each arguement to access their value.

Then validate the given arguements, particularly the soruce directory since that is where we are getting our information from.

Then pass the argument values to [`process_source_directory()`](#process_source_directory) which returns two integers representing the number of file documents the script generated, and the number of files already documented. Which are printed in the log

# process_source_directory()

**Inputs:** Given the `source_dir`, `docs_outout_dir`, and `overwrite` bool.

Uses the `os` package to get the absolute path of the source directory, and documentation directory. 

Uses [`build_type_doc_map()`](#build_type_doc_map) which returns a dictionary of class names to documentation files.

Iterates through the files in the source directory, collected through `os.walk()`. 

Creates the documentation directory, firsts get the relative directory from the root, CWD of the script, and the soruce directory. If there is no relative path then the documentation directory is created in the CWD. Otherwise it is created in the relative directory from the CWD to the source directory.

Iterate through the java files, creating the path for the documentation files, API, and SDD. Parses the Java files with `parse_java_file()`.

# build_type_doc_map()

**Inputs:** Given the `source_dir`, and `docs_output_dir` strings.

Uses the `os` package to get the absolute path of the source and documentation directories.

Iterates through all the files in the source directory, collected through an `os.walk()`. filters through only java files, this can be the location where we add other programming languages file documentation. Takes the name of each java file as a class. Then fills the class entry with the documentation file absolute path.

    For other languages we can use the file name as a component/module. With functions inside of them.

# parse_java_file()

**Inputs:** The path to the java file, `file_path`.

Opens the file using `utf-8` encoding, wraps the open attempt in a try catch to handle errors.

Splits the file into lines using `split("\n")`.

Uses regular expressions to extract the package, imports, and class declarations from the opened file.