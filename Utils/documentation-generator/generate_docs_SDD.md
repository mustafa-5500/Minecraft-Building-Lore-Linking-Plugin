# generate_docs.py — Software Detailed Design

> **API Documentation:** [generate_docs.md](./generate_docs.md)  
> **Source File:** [generate_docs.py](./generate_docs.py)

## Usage

This utility is designed for documentation generation and synchronization runs against Java and/or Python source roots:

```bash
python generate_docs.py <source_dir> <docs_output_dir> [--overwrite]
```

Run without `--overwrite` for safe merge behavior that preserves manual edits.

## Table of Contents

- [Usage](#usage)
- [1. Overview](#1-overview)
- [2. High-Level Architecture](#2-high-level-architecture)
- [3. Data Models](#3-data-models)
- [4. Java Parsing Pipeline](#4-java-parsing-pipeline)
- [5. Python Parsing Pipeline](#5-python-parsing-pipeline)
- [6. Generation Pipeline](#6-generation-pipeline)
- [7. Merge and Normalization Pipeline](#7-merge-and-normalization-pipeline)
- [8. Type-Linking Pipeline](#8-type-linking-pipeline)
- [9. File Processing Orchestration](#9-file-processing-orchestration)
- [10. CLI and Runtime Behavior](#10-cli-and-runtime-behavior)
- [11. Design Constraints and Limitations](#11-design-constraints-and-limitations)

## 1. Overview

`generate_docs.py` produces API and SDD markdown templates by extracting structural metadata from Java and Python source files. It supports both first-time generation and incremental merge updates, and keeps document structure consistent via enforced section ordering and automatic table-of-contents rebuilding.

---

## 2. High-Level Architecture

The script is organized into these functional areas:

- Metadata models (`MethodInfo`, `FieldInfo`, `JavaClassInfo`)
- Java parsing helpers (regex-based)
- Python parsing helpers (AST-based)
- Markdown generation for API and SDD outputs
- Merge logic for existing docs
- Linkification and layout normalization
- Directory traversal and per-type processing
- CLI entrypoint and summary reporting

---

## 3. Data Models

### 3.1 `MethodInfo`

Stores method/function constructor metadata used by both API and SDD writers.

Key properties:

- signature
- parameters (`(type, name)` tuples)
- return type
- parsed description
- parsed parameter and return descriptions
- annotations/decorators
- access visibility
- constructor/static flags

### 3.2 `FieldInfo`

Stores field/attribute metadata:

- field name
- field type (when available)
- access visibility
- static/final flags (primarily Java)

### 3.3 `JavaClassInfo`

Unified intermediate model used for Java classes, Python classes, and Python module-level function containers.

Notable fields:

- `language` (`java` or `python`)
- class/module declaration text
- imports list
- inheritance/base-class metadata
- optional class/module doc text (`javadoc` field)

---

## 4. Java Parsing Pipeline

### 4.1 Entry Point: `parse_java_file`

- Reads UTF-8 source content.
- Extracts package/import lines.
- Extracts the primary public class/interface/enum declaration.
- Captures class-level JavaDoc directly preceding the declaration.
- Delegates field extraction to `extract_fields`.
- Delegates method/constructor extraction to `extract_methods`.

### 4.2 Field Extraction: `extract_fields`

- Scans near class top-level region before first method signature.
- Extracts access/static/final/type/name patterns.
- Filters common keyword false positives.

### 4.3 Method Extraction: `extract_methods`

- Uses separate constructor and method regex patterns.
- Associates JavaDoc only when directly adjacent (allowing only whitespace/annotations between doc and declaration).
- Parses JavaDoc text through `_parse_java_method_doc` to fill:
  - summary description
  - per-parameter descriptions
  - return description

### 4.4 Parameter Parsing: `parse_parameters`

- Splits comma-delimited parameter lists.
- Removes inline annotations like `@NotNull`.
- Produces `(type, name)` tuples.

---

## 5. Python Parsing Pipeline

### 5.1 Entry Point: `parse_python_file`

- Parses source using Python `ast`.
- Captures imports from `import` and `from ... import ...` forms.
- Emits one `JavaClassInfo` per top-level class.
- If no top-level classes but top-level functions exist, emits one module-level `JavaClassInfo`.

### 5.2 Signature and Annotation Handling

- `_ast_annotation_to_str` serializes AST type annotations.
- `_build_python_signature` builds sync/async function signatures.
- Handles positional defaults, varargs, kw-only args, kwargs, and return annotations.
- Skips `self`/`cls` for non-static methods in displayed signature/parameter list.

### 5.3 Field/Attribute Extraction

`_extract_python_fields` collects:

- class-level assignments/annotated assignments
- instance attributes assigned in `__init__`

### 5.4 Description Extraction

- `_parse_python_docstring` parses docstring sections for:
  - summary text
  - parameter descriptions (`Args`, `Arguments`, `Parameters`)
  - return descriptions (`Return`, `Returns`)

### 5.5 Method Model Conversion

`_parse_python_func_node` maps AST function nodes into `MethodInfo`, including:

- decorator list (stored in `annotations`)
- static method detection via `@staticmethod`
- constructor detection for `__init__`
- visibility inference from underscore naming

---

## 6. Generation Pipeline

### 6.1 API Generation: `generate_api_doc`

Builds sections in this order:

- normalized header links
- `Usage`
- high-level description (doc text or TODO)
- table of contents
- optional fields section
- per-method sections
- `See Also`

Method sections include:

- signature code block (java/python)
- description
- parameters table (or `None`)
- return section with constructor/void/type-specific handling

### 6.2 SDD Generation: `generate_sdd_doc`

Builds numbered sections with language-aware wording:

- Overview
- Package Declaration & Imports (Java) or Module & Imports (Python)
- Class Declaration (Java) or Class Definition (Python)
- optional Instance Fields
- per-method numbered sections

Both generators run a final `linkify_content` pass.

---

## 7. Merge and Normalization Pipeline

### 7.1 Existing Doc Parsing

- `parse_existing_api_doc` identifies documented fields/method headings and `See Also` location.
- `parse_existing_sdd_doc` identifies documented methods and highest section number.

### 7.2 API Merge: `merge_api_doc`

- Normalizes top header block.
- Adds missing fields and methods only.
- Moves `See Also` to document end.
- Injects parsed method descriptions and parameter/return text into existing TODO placeholders.
- Enforces Usage/TOC ordering with `_enforce_usage_and_toc_layout`.

### 7.3 SDD Merge: `merge_sdd_doc`

- Appends only missing method sections.
- Continues numbering from last discovered section number.
- Injects parsed method descriptions into TODO placeholders.
- Enforces Usage/TOC ordering with `_enforce_usage_and_toc_layout`.

### 7.4 Description Injection Helpers

- `_inject_api_method_descriptions`
- `_inject_sdd_method_descriptions`

Both replace known default TODO text without removing custom authored prose outside those placeholders.

---

## 8. Type-Linking Pipeline

### 8.1 Type Map Construction

`build_type_doc_map` creates a `type -> doc path` map from source traversal:

- Java: file name minus `.java`
- Python: discovered class names, or module name if classless

### 8.2 Structured Link Resolution

`resolve_type_link` links field/parameter/return types by:

- stripping generic/array wrappers for lookup
- skipping self-links
- returning relative markdown links when targets exist

### 8.3 Inline Linkification

`linkify_inline_types` and `linkify_content`:

- convert backtick-wrapped type mentions in prose into links
- skip already linked references
- skip fenced code blocks

---

## 9. File Processing Orchestration

### 9.1 Per-Type Workflow: `_process_class_info`

For each parsed `JavaClassInfo`:

- computes target API + SDD paths
- computes relative source path
- executes one of:
  - overwrite create path
  - merge path when both docs exist
  - partial create path when one is missing

### 9.2 Directory Walk: `process_source_directory`

- traverses all subfolders under source root
- filters `.java` and `.py`
- parses each file into one or more `JavaClassInfo` objects
- processes each object independently
- tracks generated/skipped counters

The counter granularity is type/module pair level, not just source file level.

---

## 10. CLI and Runtime Behavior

### 10.1 `main`

- parses positional arguments and `--overwrite`
- validates source directory exists
- prints configuration summary
- runs processing pipeline
- prints final generated/skipped summary

### 10.2 Status Emission

During execution, the script logs statuses per output file:

- `CREATED`
- `MERGED`
- `UP-TO-DATE`
- `WARN` (parse failures)

---

## 11. Design Constraints and Limitations

- Java parsing is regex-based and targets common declaration forms.
- Python parsing assumes valid syntax (`ast.parse`), otherwise file is skipped with warning.
- Java method annotation capture is limited to single-line patterns adjacent to declarations.
- Java parser still focuses on one primary public declaration per file.
- Type linking is project-internal only (types outside discovered map remain plain backticks).
- Existing authored documentation is preserved by design unless `--overwrite` is used.
