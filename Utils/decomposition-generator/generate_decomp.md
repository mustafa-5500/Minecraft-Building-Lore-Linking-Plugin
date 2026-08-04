# generate_decomp

> **Software Detailed Documentation:** [generate_decomp_SDD.md](./generate_decomp_SDD.md)  
> **Source File:** [generate_decomp.py](generate_decomp.py)

## Table of Contents

- [Usage](#usage)
- [Imports](#imports)
- [Classes](#classes)
- [Module Functions](#module-functions)
- [See Also](#see-also)


## Usage

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

## Imports

- `os`
- `sys`
- `re`
- `ast`
- `pathlib.Path`

## Classes

### Class [`PythonMethodCallVisitor`](generate_decomp.md)

#### Declaration
```python
class PythonMethodCallVisitor(ast.NodeVisitor):
```

TODO: Add description for class [`PythonMethodCallVisitor`](generate_decomp.md).

#### Fields

| Name | Type | Description |
|------|------|-------------|
| `method_calls` | `dict[str, list[str]]` | TODO: describe field |
| `local_methods` | `set[str]` | TODO: describe field |
| `_function_stack` | `list[str]` | TODO: describe field |
| `_class_stack` | `list[str]` | TODO: describe field |

#### Methods

##### PythonMethodCallVisitor.__init__

```python
def __init__() -> None:
```

TODO: Describe what `PythonMethodCallVisitor.__init__` does.

##### PythonMethodCallVisitor.current_function

```python
def current_function() -> str | None:
```

TODO: Describe what `PythonMethodCallVisitor.current_function` does.

##### PythonMethodCallVisitor.visit_ClassDef

```python
def visit_ClassDef(node: ast.ClassDef) -> None:
```

TODO: Describe what `PythonMethodCallVisitor.visit_ClassDef` does.

##### PythonMethodCallVisitor.visit_FunctionDef

```python
def visit_FunctionDef(node: ast.FunctionDef) -> None:
```

TODO: Describe what `PythonMethodCallVisitor.visit_FunctionDef` does.

##### PythonMethodCallVisitor.visit_AsyncFunctionDef

```python
def visit_AsyncFunctionDef(node: ast.AsyncFunctionDef) -> None:
```

TODO: Describe what `PythonMethodCallVisitor.visit_AsyncFunctionDef` does.

##### PythonMethodCallVisitor._visit_function

```python
def _visit_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
```

TODO: Describe what `PythonMethodCallVisitor._visit_function` does.

##### PythonMethodCallVisitor.visit_Call

```python
def visit_Call(node: ast.Call) -> None:
```

TODO: Describe what `PythonMethodCallVisitor.visit_Call` does.

## Module Functions

### usage

```python
def usage() -> None:
```

Print usage information for the script.

### collect_source_files

```python
def collect_source_files(source_root: Path) -> list[Path]:
```

Collect all supported source files from the given source root directory.

### strip_comments_and_strings

```python
def strip_comments_and_strings(code: str) -> str:
```

TODO: Describe what `strip_comments_and_strings` does.

### find_matching_brace

```python
def find_matching_brace(text: str, open_brace_idx: int) -> int:
```

TODO: Describe what `find_matching_brace` does.

### class_names

```python
def class_names(code: str) -> set[str]:
```

TODO: Describe what `class_names` does.

### is_probable_method_declaration

```python
def is_probable_method_declaration(prefix: str, name: str, declared_types: set[str]) -> bool:
```

TODO: Describe what `is_probable_method_declaration` does.

### extract_methods

```python
def extract_methods(cleaned_code: str) -> list[tuple[str, int, int]]:
```

TODO: Describe what `extract_methods` does.

### extract_calls

```python
def extract_calls(method_body: str) -> list[str]:
```

TODO: Describe what `extract_calls` does.

### attribute_chain_name

```python
def attribute_chain_name(node: ast.AST) -> str | None:
```

TODO: Describe what `attribute_chain_name` does.

### simple_callable_name

```python
def simple_callable_name(node: ast.AST) -> str | None:
```

TODO: Describe what `simple_callable_name` does.

### analyze_python_source

```python
def analyze_python_source(code: str) -> tuple[dict[str, list[str]], set[str]]:
```

TODO: Describe what `analyze_python_source` does.

### analyze_java_source

```python
def analyze_java_source(code: str) -> tuple[dict[str, list[str]], set[str]]:
```

TODO: Describe what `analyze_java_source` does.

### sanitize_identifier

```python
def sanitize_identifier(value: str) -> str:
```

TODO: Describe what `sanitize_identifier` does.

### simple_name

```python
def simple_name(symbol: str) -> str:
```

TODO: Describe what `simple_name` does.

### filter_method_calls

```python
def filter_method_calls(method_calls: dict[str, list[str]], local_methods: set[str], global_project_callables: set[str], verbose: bool) -> dict[str, list[str]]:
```

TODO: Describe what `filter_method_calls` does.

### load_theme_lines

```python
def load_theme_lines(script_root: Path, theme: str) -> list[str]:
```

TODO: Describe what `load_theme_lines` does.

### build_puml

```python
def build_puml(relative_path: Path, method_calls: dict[str, list[str]], local_methods: set[str], theme_lines: list[str]) -> str:
```

TODO: Describe what `build_puml` does.

### analyze_file

```python
def analyze_file(source_file: Path, source_root: Path) -> tuple[Path, dict[str, list[str]], set[str]]:
```

TODO: Describe what `analyze_file` does.

### write_output

```python
def write_output(output_root: Path, relative_source: Path, diagram: str, suffix: str = '') -> Path:
```

TODO: Describe what `write_output` does.

### main

```python
def main() -> int:
```

TODO: Describe what `main` does.

## See Also

- **Software Detailed Design:** [generate_decomp_SDD.md](./generate_decomp_SDD.md)