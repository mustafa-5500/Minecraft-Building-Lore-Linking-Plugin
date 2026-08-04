# generate_decomp — Software Detailed Design

> **API Documentation:** [generate_decomp.md](./generate_decomp.md)  
> **Source File:** [generate_decomp.py](generate_decomp.py)

## Table of Contents

- [Usage](#usage)
- [1. Overview](#1-overview)
- [2. Imports](#2-imports)
- [3. Classes](#3-classes)
- [4. Module-Level Functions](#4-module-level-functions)


## Usage

TODO: Describe how `generate_decomp` is used.

---

## 1. Overview

Decomposition Diagram Generator for Java and Python Projects.

Given a source code directory and documentation output folder, this script
generates a decomposition diagram in PlantUML format for each supported source
file. The diagrams show function-call flow for each file.

Usage:
    python generate_decomp.py <source_code_directory> <documentation_output_folder> [theme] [verbose]

Theme values:
    light | dark | both | none

Optional flag:
    verbose (or --verbose, -v)

Example:
    python generate_decomp.py ../src/main/java/org/almond/buildinglore ../Documentation both verbose

---

## 2. Imports

```python
import os
import sys
import re
import ast
from pathlib import Path
```

---

## 3. Classes

### [`PythonMethodCallVisitor`](generate_decomp.md)

```python
class PythonMethodCallVisitor(ast.NodeVisitor):
```

TODO: Explain class [`PythonMethodCallVisitor`](generate_decomp.md).

#### Fields

- `method_calls` (`dict[str, list[str]]`) — TODO: describe
- `local_methods` (`set[str]`) — TODO: describe
- `_function_stack` (`list[str]`) — TODO: describe
- `_class_stack` (`list[str]`) — TODO: describe

#### Methods

```python
def __init__() -> None:
```
TODO: Provide detailed design for `PythonMethodCallVisitor.__init__`.

```python
def current_function() -> str | None:
```
TODO: Provide detailed design for `PythonMethodCallVisitor.current_function`.

```python
def visit_ClassDef(node: ast.ClassDef) -> None:
```
TODO: Provide detailed design for `PythonMethodCallVisitor.visit_ClassDef`.

```python
def visit_FunctionDef(node: ast.FunctionDef) -> None:
```
TODO: Provide detailed design for `PythonMethodCallVisitor.visit_FunctionDef`.

```python
def visit_AsyncFunctionDef(node: ast.AsyncFunctionDef) -> None:
```
TODO: Provide detailed design for `PythonMethodCallVisitor.visit_AsyncFunctionDef`.

```python
def _visit_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
```
TODO: Provide detailed design for `PythonMethodCallVisitor._visit_function`.

```python
def visit_Call(node: ast.Call) -> None:
```
TODO: Provide detailed design for `PythonMethodCallVisitor.visit_Call`.

---

## 4. Module-Level Functions

### `usage()`

```python
def usage() -> None:
```
Print usage information for the script.

### `collect_source_files()`

```python
def collect_source_files(source_root: Path) -> list[Path]:
```
Collect all supported source files from the given source root directory.

### `strip_comments_and_strings()`

```python
def strip_comments_and_strings(code: str) -> str:
```
TODO: Provide detailed design for `strip_comments_and_strings`.

### `find_matching_brace()`

```python
def find_matching_brace(text: str, open_brace_idx: int) -> int:
```
TODO: Provide detailed design for `find_matching_brace`.

### `class_names()`

```python
def class_names(code: str) -> set[str]:
```
TODO: Provide detailed design for `class_names`.

### `is_probable_method_declaration()`

```python
def is_probable_method_declaration(prefix: str, name: str, declared_types: set[str]) -> bool:
```
TODO: Provide detailed design for `is_probable_method_declaration`.

### `extract_methods()`

```python
def extract_methods(cleaned_code: str) -> list[tuple[str, int, int]]:
```
TODO: Provide detailed design for `extract_methods`.

### `extract_calls()`

```python
def extract_calls(method_body: str) -> list[str]:
```
TODO: Provide detailed design for `extract_calls`.

### `attribute_chain_name()`

```python
def attribute_chain_name(node: ast.AST) -> str | None:
```
TODO: Provide detailed design for `attribute_chain_name`.

### `simple_callable_name()`

```python
def simple_callable_name(node: ast.AST) -> str | None:
```
TODO: Provide detailed design for `simple_callable_name`.

### `analyze_python_source()`

```python
def analyze_python_source(code: str) -> tuple[dict[str, list[str]], set[str]]:
```
TODO: Provide detailed design for `analyze_python_source`.

### `analyze_java_source()`

```python
def analyze_java_source(code: str) -> tuple[dict[str, list[str]], set[str]]:
```
TODO: Provide detailed design for `analyze_java_source`.

### `sanitize_identifier()`

```python
def sanitize_identifier(value: str) -> str:
```
TODO: Provide detailed design for `sanitize_identifier`.

### `simple_name()`

```python
def simple_name(symbol: str) -> str:
```
TODO: Provide detailed design for `simple_name`.

### `filter_method_calls()`

```python
def filter_method_calls(method_calls: dict[str, list[str]], local_methods: set[str], global_project_callables: set[str], verbose: bool) -> dict[str, list[str]]:
```
TODO: Provide detailed design for `filter_method_calls`.

### `load_theme_lines()`

```python
def load_theme_lines(script_root: Path, theme: str) -> list[str]:
```
TODO: Provide detailed design for `load_theme_lines`.

### `build_puml()`

```python
def build_puml(relative_path: Path, method_calls: dict[str, list[str]], local_methods: set[str], theme_lines: list[str]) -> str:
```
TODO: Provide detailed design for `build_puml`.

### `analyze_file()`

```python
def analyze_file(source_file: Path, source_root: Path) -> tuple[Path, dict[str, list[str]], set[str]]:
```
TODO: Provide detailed design for `analyze_file`.

### `write_output()`

```python
def write_output(output_root: Path, relative_source: Path, diagram: str, suffix: str = '') -> Path:
```
TODO: Provide detailed design for `write_output`.

### `main()`

```python
def main() -> int:
```
TODO: Provide detailed design for `main`.