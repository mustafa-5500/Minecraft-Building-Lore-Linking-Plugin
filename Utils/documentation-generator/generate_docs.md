# generate_docs.py

> **Software Detailed Documentation:** [generate_docs_SDD.md](./generate_docs_SDD.md)  
> **Source File:** [generate_docs.py](./generate_docs.py)

Generates and updates API and SDD markdown templates from Java and Python source trees. The script mirrors source folders in the docs output folder, links related types, and merges changes into existing documentation without removing manual content.

## Usage

```bash
python generate_docs.py <source_dir> <docs_output_dir> [--overwrite]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `source_dir` | Yes | Root source directory containing `.java` and/or `.py` files. |
| `docs_output_dir` | Yes | Root documentation output directory. |
| `--overwrite` | No | Regenerates both docs for every parsed type/module pair. Without this flag, existing docs are merged and preserved. |

### Examples

Generate/merge Java docs:
```bash
python Utils/documentation-generator/generate_docs.py src/main/java/org/almond/buildinglore Documentation
```

Generate/merge Python docs:
```bash
python Utils/documentation-generator/generate_docs.py src/main/python/org/almond/buildinglore Documentation
```

Regenerate everything:
```bash
python Utils/documentation-generator/generate_docs.py src/main/java/org/almond/buildinglore Documentation --overwrite
```

## Table of Contents

- [Usage](#usage)
- [Output](#output)
- [Core Behavior](#core-behavior)
- [Merge Behavior](#merge-behavior)
- [Cross-Reference Linking](#cross-reference-linking)
- [Console Output](#console-output)
- [Dependencies](#dependencies)

## Output

For each discovered type, the script writes two files in the mirrored docs folder:

- `[TypeName].md` (API doc)
- `[TypeName]_SDD.md` (SDD doc)

### Java Input

- One top-level `.java` class/interface/enum file yields one API/SDD pair.

### Python Input

- A `.py` file with top-level classes yields one API/SDD pair per class.
- A `.py` file with no top-level classes but with top-level functions yields one API/SDD pair for the module name.

## Core Behavior

- Supports both `.java` and `.py` discovery in one run.
- Mirrors source directory structure under the docs output root.
- Computes source file links relative to each generated doc file.
- Parses Java signatures with regex and Python signatures with `ast`.
- Extracts method/function descriptions from:
  - JavaDoc (`@param`, `@return`, multiline support)
  - Python docstrings (`Args/Arguments/Parameters`, `Returns` sections)
- Populates API parameter and return descriptions when parsed metadata exists.
- Populates SDD method description placeholders when parsed metadata exists.
- Enforces generated/merged doc layout as:
  - Header block
  - `## Usage`
  - `## Table of Contents`
  - Remaining sections

## Merge Behavior

Default mode merges into existing docs when both API and SDD files exist for a type.

- Adds newly discovered fields to API `## Fields`.
- Adds newly discovered methods/constructors as new sections.
- Preserves existing authored text.
- Normalizes API header to current format.
- Repositions `## See Also` to the end of API docs.
- Rebuilds table of contents from current `##` headings.
- Ensures `## Usage` and `## Table of Contents` are present and ordered.
- Runs a linkification pass even when no structural merge was needed.

If only one of the two files exists, the missing file is created.

With `--overwrite`, both files are rewritten for each parsed type.

## Cross-Reference Linking

The script builds a type-to-doc map from source discovery and applies linking in two ways:

- Structured type links:
  - Field types
  - Parameter types
  - Return types
- Inline backtick linkification in non-code blocks:
  - Converts `` `TypeName` `` to `` [`TypeName`](relative/path.md) `` when a doc target exists.

Linking behavior details:

- Skips self-links (type is the current class/module).
- Preserves code blocks (no inline link replacement inside fenced blocks).
- Resolves relative links from each current doc directory.
- Handles generic/array stripping to resolve base type names.

## Console Output

Typical statuses:

- `CREATED`: new API or SDD file written.
- `MERGED`: existing file changed through merge/normalization.
- `UP-TO-DATE`: both files already in sync after merge checks.
- `WARN`: parser could not produce metadata for a file.

Summary line:

```text
Done. Generated: <N> file pairs, Skipped: <M> (already exist)
```

Counts are tracked per processed type/module pair, not strictly per source file.

## Dependencies

Standard library only.

| Module | Purpose |
|--------|---------|
| `argparse` | CLI argument parsing |
| `ast` | Python source parsing |
| `dataclasses` | Structured parse models |
| `os` | File walking, path handling, output writing |
| `re` | Java parsing and markdown/link processing |
| `sys` | Exit on invalid source directory |
| `typing` | Type hints |
| `pathlib.Path` | Path utilities (imported) |

No third-party dependencies are required.
