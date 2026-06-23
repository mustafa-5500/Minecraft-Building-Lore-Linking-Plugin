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

# build_type_doc_map()

