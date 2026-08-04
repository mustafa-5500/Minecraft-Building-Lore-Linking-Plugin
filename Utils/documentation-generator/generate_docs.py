"""
Documentation Template Generator for Java and Python Plugin Projects.

Given a source code directory and documentation output folder,
this script generates template .md and _SDD.md documentation files mirroring
the source folder structure. Templates follow the existing documentation format.

Supports Java (.java) and Python (.py) source files.

Usage:
    python generate_docs.py <source_dir> <docs_output_dir>

Example:
    python generate_docs.py ../src/main/java/org/almond/buildinglore ../Documentation
    python generate_docs.py ../src/main/python/org/almond/buildinglore ../Documentation
"""

import ast
import os
import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MethodInfo:
    name: str
    signature: str
    return_type: str
    parameters: List[tuple]  # [(type, name), ...]
    description: Optional[str] = None
    parameter_descriptions: Dict[str, str] = field(default_factory=dict)
    return_description: Optional[str] = None
    annotations: List[str] = field(default_factory=list)
    access: str = "public"
    is_static: bool = False
    is_constructor: bool = False


@dataclass
class FieldInfo:
    name: str
    type: str
    access: str = "private"
    is_static: bool = False
    is_final: bool = False


@dataclass
class JavaClassInfo:
    name: str
    file_name: str
    package: str
    imports: List[str]
    class_declaration: str
    fields: List[FieldInfo]
    methods: List[MethodInfo]
    extends_class: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    javadoc: Optional[str] = None
    language: str = "java"


@dataclass
class PythonClassDoc:
    name: str
    class_declaration: str
    fields: List[FieldInfo]
    methods: List[MethodInfo]
    bases: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class PythonModuleDoc:
    module_name: str
    file_name: str
    imports: List[str]
    classes: List[PythonClassDoc]
    functions: List[MethodInfo]
    module_docstring: Optional[str] = None


def _parse_python_docstring(doc: Optional[str]) -> tuple:
    """Parse Python docstring into summary, parameter descriptions, and return description."""
    if not doc:
        return None, {}, None

    lines = [line.rstrip() for line in doc.expandtabs().splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    summary_lines = []
    param_desc: Dict[str, str] = {}
    return_desc_lines = []
    section = "summary"
    current_param = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        lowered = stripped.lower()

        if lowered in ("args:", "arguments:", "arguements:", "parameters:"):
            section = "params"
            current_param = None
            i += 1
            continue
        if lowered in ("return:", "returns:"):
            section = "returns"
            current_param = None
            i += 1
            continue
        if re.match(r"^[A-Za-z ]+:$", stripped) and lowered not in ("args:", "arguments:", "arguements:", "parameters:", "return:", "returns:"):
            section = "other"
            current_param = None
            i += 1
            continue

        if section == "summary":
            summary_lines.append(line)
        elif section == "params":
            param_match = re.match(r"^\s*([*]{0,2}[A-Za-z_][\w]*)\s*(?:\([^)]*\))?\s*:\s*(.*)$", line)
            if param_match:
                current_param = param_match.group(1).lstrip("*")
                desc = param_match.group(2).strip()
                param_desc[current_param] = desc
            elif current_param and line.startswith(" "):
                extra = stripped
                if extra:
                    existing = param_desc.get(current_param, "")
                    param_desc[current_param] = f"{existing} {extra}".strip()
        elif section == "returns":
            if stripped:
                return_desc_lines.append(stripped)

        i += 1

    summary = "\n".join(summary_lines).strip() or None
    ret_desc = " ".join(return_desc_lines).strip() or None
    return summary, param_desc, ret_desc


def _parse_java_method_doc(doc: Optional[str]) -> tuple:
    """Parse JavaDoc text into summary, parameter descriptions, and return description."""
    if not doc:
        return None, {}, None

    lines = [line.rstrip() for line in doc.splitlines()]
    summary_lines = []
    param_desc: Dict[str, str] = {}
    return_desc = None
    current_tag = None
    current_param = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_tag is None:
                summary_lines.append("")
            continue

        param_match = re.match(r"^@param\s+(\w+)\s*(.*)$", stripped)
        if param_match:
            current_tag = "param"
            current_param = param_match.group(1)
            param_desc[current_param] = param_match.group(2).strip()
            continue

        return_match = re.match(r"^@return\s*(.*)$", stripped)
        if return_match:
            current_tag = "return"
            current_param = None
            return_desc = return_match.group(1).strip()
            continue

        if stripped.startswith("@"):
            current_tag = "other"
            current_param = None
            continue

        if current_tag == "param" and current_param:
            param_desc[current_param] = f"{param_desc.get(current_param, '')} {stripped}".strip()
        elif current_tag == "return":
            return_desc = f"{(return_desc or '')} {stripped}".strip()
        else:
            summary_lines.append(line)

    summary = "\n".join(summary_lines).strip() or None
    return summary, param_desc, (return_desc or None)


def parse_java_file(file_path: str) -> Optional[JavaClassInfo]:
    """Parse a Java file and extract class information."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, UnicodeDecodeError):
        return None

    lines = content.split("\n")

    # Extract package
    package = ""
    pkg_match = re.search(r"^package\s+([\w.]+)\s*;", content, re.MULTILINE)
    if pkg_match:
        package = pkg_match.group(1)

    # Extract imports
    imports = re.findall(r"^import\s+([\w.*]+)\s*;", content, re.MULTILINE)

    # Extract class declaration
    class_match = re.search(
        r"(public\s+(?:abstract\s+)?(?:final\s+)?(?:class|interface|enum)\s+"
        r"(\w+)(?:\s+extends\s+([\w<>,\s]+?))?(?:\s+implements\s+([\w<>,\s]+?))?\s*\{)",
        content,
    )

    if not class_match:
        return None

    class_declaration = class_match.group(1)
    class_name = class_match.group(2)
    extends_class = class_match.group(3).strip() if class_match.group(3) else None
    implements_raw = class_match.group(4)
    implements = (
        [i.strip() for i in implements_raw.split(",")]
        if implements_raw
        else []
    )

    # Extract class-level javadoc (immediately before class declaration)
    javadoc = None
    class_line_idx = content.find(class_match.group(0))
    before_class = content[:class_line_idx].rstrip()
    javadoc_match = re.search(r"/\*\*(.*?)\*/\s*$", before_class, re.DOTALL)
    if javadoc_match:
        raw = javadoc_match.group(1)
        javadoc = re.sub(r"^\s*\*\s?", "", raw, flags=re.MULTILINE).strip()

    # Extract fields
    fields = extract_fields(content, class_match.end())

    # Extract methods
    methods = extract_methods(content, class_name)

    file_name = os.path.basename(file_path)

    return JavaClassInfo(
        name=class_name,
        file_name=file_name,
        package=package,
        imports=imports,
        class_declaration=class_declaration,
        fields=fields,
        methods=methods,
        extends_class=extends_class,
        implements=implements,
        javadoc=javadoc,
    )


def extract_fields(content: str, class_body_start: int) -> List[FieldInfo]:
    """Extract field declarations from the class body."""
    fields = []
    # Match field declarations (not inside methods)
    # Look for lines like: private final Type name; or private Type name = ...;
    field_pattern = re.compile(
        r"^\s*((?:private|protected|public)\s+)?"
        r"(static\s+)?(final\s+)?"
        r"([\w<>\[\],\s]+?)\s+"
        r"(\w+)\s*(?:=|;)",
        re.MULTILINE,
    )

    # Only look at the top-level of the class (before first method)
    # Find the first method start
    method_start = re.search(
        r"(?:(?:public|private|protected)\s+)?(?:static\s+)?(?:synchronized\s+)?"
        r"(?:[\w<>\[\],\s]+?)\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{",
        content[class_body_start:],
    )

    search_region = (
        content[class_body_start : class_body_start + method_start.start()]
        if method_start
        else content[class_body_start : class_body_start + 500]
    )

    for match in field_pattern.finditer(search_region):
        access = (match.group(1) or "package-private").strip()
        is_static = bool(match.group(2))
        is_final = bool(match.group(3))
        field_type = match.group(4).strip()
        field_name = match.group(5).strip()

        # Skip common false positives
        if field_type in ("return", "if", "for", "while", "new", "class", "import"):
            continue

        fields.append(
            FieldInfo(
                name=field_name,
                type=field_type,
                access=access,
                is_static=is_static,
                is_final=is_final,
            )
        )

    return fields


def extract_methods(content: str, class_name: str) -> List[MethodInfo]:
    """Extract method signatures from the class."""
    methods = []

    def clean_javadoc(raw: str) -> str:
        """Normalize a JavaDoc block body into plain markdown text."""
        return re.sub(r"^\s*\*\s?", "", raw, flags=re.MULTILINE).strip()

    def extract_method_javadoc(start_idx: int) -> Optional[str]:
        """Extract JavaDoc immediately preceding a method/constructor declaration."""
        prefix = content[:start_idx]
        last_match = None
        for match in re.finditer(r"/\*\*(.*?)\*/", prefix, re.DOTALL):
            last_match = match

        if not last_match:
            return None

        between = prefix[last_match.end():]
        # Allow only whitespace and annotations between JavaDoc and declaration.
        if not re.match(r"^\s*(?:@\w+(?:\([^)]*\))?\s*)*$", between, re.DOTALL):
            return None

        return clean_javadoc(last_match.group(1))

    # Pattern for method declarations
    method_pattern = re.compile(
        r"(?:(@\w+(?:\([^)]*\))?)\s+)?"  # optional annotation
        r"(public|private|protected)\s+"
        r"(static\s+)?"
        r"(?:synchronized\s+)?"
        r"([\w<>\[\],?\s]+?)\s+"  # return type
        r"(\w+)\s*"  # method name
        r"\(([^)]*)\)\s*"  # parameters
        r"(?:throws\s+[\w,\s]+)?\s*\{",
        re.MULTILINE,
    )

    # Also match constructors
    constructor_pattern = re.compile(
        r"(?:(@\w+(?:\([^)]*\))?)\s+)?"
        r"(public|private|protected)\s+"
        + re.escape(class_name)
        + r"\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*\{",
        re.MULTILINE,
    )

    # Find constructors
    for match in constructor_pattern.finditer(content):
        annotation = match.group(1) or ""
        access = match.group(2)
        params_raw = match.group(3).strip()
        parameters = parse_parameters(params_raw)
        raw_doc = extract_method_javadoc(match.start())
        description, parameter_descriptions, return_description = _parse_java_method_doc(raw_doc)

        annotations = [annotation] if annotation else []
        sig = f"{access} {class_name}({params_raw})"

        methods.append(
            MethodInfo(
                name=class_name,
                signature=sig,
                return_type="",
                parameters=parameters,
                description=description,
                parameter_descriptions=parameter_descriptions,
                return_description=return_description,
                annotations=annotations,
                access=access,
                is_static=False,
                is_constructor=True,
            )
        )

    # Find methods
    for match in method_pattern.finditer(content):
        annotation = match.group(1) or ""
        access = match.group(2)
        is_static = bool(match.group(3))
        return_type = match.group(4).strip()
        method_name = match.group(5).strip()
        params_raw = match.group(6).strip()
        raw_doc = extract_method_javadoc(match.start())
        description, parameter_descriptions, return_description = _parse_java_method_doc(raw_doc)

        # Skip if this is actually a constructor (caught above)
        if method_name == class_name:
            continue

        parameters = parse_parameters(params_raw)
        annotations = [annotation] if annotation else []

        static_str = "static " if is_static else ""
        sig = f"{access} {static_str}{return_type} {method_name}({params_raw})"

        methods.append(
            MethodInfo(
                name=method_name,
                signature=sig,
                return_type=return_type,
                parameters=parameters,
                description=description,
                parameter_descriptions=parameter_descriptions,
                return_description=return_description,
                annotations=annotations,
                access=access,
                is_static=is_static,
                is_constructor=False,
            )
        )

    return methods


def parse_parameters(params_raw: str) -> List[tuple]:
    """Parse a parameter string into a list of (type, name) tuples."""
    if not params_raw:
        return []

    params = []
    for param in params_raw.split(","):
        param = param.strip()
        if not param:
            continue
        # Handle annotations in params (e.g., @NotNull String name)
        param = re.sub(r"@\w+\s+", "", param)
        parts = param.rsplit(" ", 1)
        if len(parts) == 2:
            params.append((parts[0].strip(), parts[1].strip()))
        else:
            params.append((param, ""))

    return params


# =============================================================================
# Python Parsing
# =============================================================================


def _ast_annotation_to_str(node) -> str:
    """Convert an AST type annotation node to its string representation."""
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return repr(node.value) if isinstance(node.value, str) else str(node.value)
    if isinstance(node, ast.Attribute):
        return f"{_ast_annotation_to_str(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return f"{_ast_annotation_to_str(node.value)}[{_ast_annotation_to_str(node.slice)}]"
    if isinstance(node, ast.Tuple):
        return ", ".join(_ast_annotation_to_str(e) for e in node.elts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return f"{_ast_annotation_to_str(node.left)} | {_ast_annotation_to_str(node.right)}"
    if isinstance(node, ast.List):
        return f"[{', '.join(_ast_annotation_to_str(e) for e in node.elts)}]"
    try:
        return ast.unparse(node)
    except AttributeError:
        return "Any"


def _build_python_signature(func_node, skip_first: bool = True) -> tuple:
    """Build a Python function signature string and extract (type, name) parameter list.

    Returns (signature_str, parameters_list, return_type_str).
    Skips the first positional argument (``self`` / ``cls``) when *skip_first* is True.
    """
    args = func_node.args
    sig_parts = []
    param_list: List[tuple] = []

    all_positional = list(args.args)
    defaults_offset = len(all_positional) - len(args.defaults)

    for i, arg in enumerate(all_positional):
        if skip_first and i == 0 and arg.arg in ("self", "cls"):
            continue
        arg_type = _ast_annotation_to_str(arg.annotation)
        default_idx = i - defaults_offset
        if default_idx >= 0:
            default_node = args.defaults[default_idx]
            if isinstance(default_node, ast.Constant):
                default_str = repr(default_node.value)
            elif isinstance(default_node, ast.Name):
                default_str = default_node.id
            else:
                default_str = "..."
            part = f"{arg.arg}: {arg_type} = {default_str}" if arg_type else f"{arg.arg} = {default_str}"
        else:
            part = f"{arg.arg}: {arg_type}" if arg_type else arg.arg
        sig_parts.append(part)
        param_list.append((arg_type, arg.arg))

    if args.vararg:
        vtype = _ast_annotation_to_str(args.vararg.annotation)
        sig_parts.append(f"*{args.vararg.arg}: {vtype}" if vtype else f"*{args.vararg.arg}")
        param_list.append((f"*{vtype}" if vtype else "*", args.vararg.arg))

    for arg in args.kwonlyargs:
        arg_type = _ast_annotation_to_str(arg.annotation)
        sig_parts.append(f"{arg.arg}: {arg_type}" if arg_type else arg.arg)
        param_list.append((arg_type, arg.arg))

    if args.kwarg:
        ktype = _ast_annotation_to_str(args.kwarg.annotation)
        sig_parts.append(f"**{args.kwarg.arg}: {ktype}" if ktype else f"**{args.kwarg.arg}")
        param_list.append((f"**{ktype}" if ktype else "**", args.kwarg.arg))

    return_type = _ast_annotation_to_str(func_node.returns)
    ret_suffix = f" -> {return_type}" if return_type else ""
    func_kw = "async def" if isinstance(func_node, ast.AsyncFunctionDef) else "def"
    signature = f"{func_kw} {func_node.name}({', '.join(sig_parts)}){ret_suffix}:"

    return signature, param_list, return_type


def _extract_python_fields(class_node: ast.ClassDef) -> List[FieldInfo]:
    """Extract class-level variables and ``__init__`` instance attributes."""
    fields: List[FieldInfo] = []
    seen: set = set()

    # Class-level declarations
    for node in class_node.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if name not in seen:
                ftype = _ast_annotation_to_str(node.annotation)
                access = "private" if name.startswith("_") else "public"
                fields.append(FieldInfo(name=name, type=ftype, access=access))
                seen.add(name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (isinstance(target, ast.Name) and
                        not target.id.startswith("__") and
                        target.id not in seen):
                    access = "private" if target.id.startswith("_") else "public"
                    fields.append(FieldInfo(name=target.id, type="", access=access))
                    seen.add(target.id)

    # Instance attributes from __init__
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "__init__":
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.AnnAssign):
                    if (isinstance(stmt.target, ast.Attribute) and
                            isinstance(stmt.target.value, ast.Name) and
                            stmt.target.value.id == "self" and
                            stmt.target.attr not in seen):
                        attr_name = stmt.target.attr
                        attr_type = _ast_annotation_to_str(stmt.annotation)
                        access = "private" if attr_name.startswith("_") else "public"
                        fields.append(FieldInfo(name=attr_name, type=attr_type, access=access))
                        seen.add(attr_name)
                elif isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if (isinstance(target, ast.Attribute) and
                                isinstance(target.value, ast.Name) and
                                target.value.id == "self" and
                                not target.attr.startswith("__") and
                                target.attr not in seen):
                            access = "private" if target.attr.startswith("_") else "public"
                            fields.append(FieldInfo(name=target.attr, type="", access=access))
                            seen.add(target.attr)
    return fields


def _parse_python_func_node(func_node) -> MethodInfo:
    """Convert an AST function/method node into a ``MethodInfo``."""
    decorators = []
    is_static = False
    for dec in func_node.decorator_list:
        if isinstance(dec, ast.Name):
            decorators.append(f"@{dec.id}")
            if dec.id == "staticmethod":
                is_static = True
        elif isinstance(dec, ast.Attribute):
            decorators.append(f"@{dec.attr}")

    is_constructor = func_node.name == "__init__"
    # Static methods keep all args; others skip self/cls
    signature, param_list, return_type = _build_python_signature(
        func_node, skip_first=not is_static
    )

    name = func_node.name
    if name.startswith("__") and name.endswith("__"):
        access = "public"
    elif name.startswith("_"):
        access = "private"
    else:
        access = "public"

    raw_doc = ast.get_docstring(func_node)
    description, parameter_descriptions, return_description = _parse_python_docstring(raw_doc)

    return MethodInfo(
        name=name,
        signature=signature,
        return_type=return_type,
        parameters=param_list,
        description=description,
        parameter_descriptions=parameter_descriptions,
        return_description=return_description,
        annotations=decorators,
        access=access,
        is_static=is_static,
        is_constructor=is_constructor,
    )


def _parse_python_class_node(class_node: ast.ClassDef) -> PythonClassDoc:
    """Convert an AST ``ClassDef`` node into a ``PythonClassDoc``."""
    class_name = class_node.name
    bases = []
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{_ast_annotation_to_str(base.value)}.{base.attr}")

    class_decl = f"class {class_name}({', '.join(bases)}):" if bases else f"class {class_name}:"
    fields = _extract_python_fields(class_node)
    methods = [
        _parse_python_func_node(n)
        for n in class_node.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    return PythonClassDoc(
        name=class_name,
        class_declaration=class_decl,
        fields=fields,
        methods=methods,
        bases=bases,
        docstring=ast.get_docstring(class_node),
    )


def parse_python_file(file_path: str) -> Optional[PythonModuleDoc]:
    """Parse a Python source file into a single module-level documentation model."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except (IOError, SyntaxError, UnicodeDecodeError):
        return None

    file_name = os.path.basename(file_path)
    module_name = file_name[:-3]  # strip .py

    imports: List[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)

    top_classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    top_functions = [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    classes = [_parse_python_class_node(cls) for cls in top_classes]
    functions = [_parse_python_func_node(fn) for fn in top_functions]

    return PythonModuleDoc(
        module_name=module_name,
        file_name=file_name,
        imports=imports,
        classes=classes,
        functions=functions,
        module_docstring=ast.get_docstring(tree),
    )


def build_type_doc_map(source_dir: str, docs_output_dir: str) -> dict:
    """Build a mapping of class/module name -> doc path for all Java and Python files."""
    source_dir = os.path.abspath(source_dir)
    docs_output_dir = os.path.abspath(docs_output_dir)
    type_map = {}  # name -> absolute path of its .md doc file

    for root, dirs, files in os.walk(source_dir):
        rel_dir = os.path.relpath(root, source_dir)
        out_dir = docs_output_dir if rel_dir == "." else os.path.join(docs_output_dir, rel_dir)

        for fname in files:
            if fname.endswith(".java"):
                class_name = fname[:-5]
                type_map[class_name] = os.path.abspath(os.path.join(out_dir, f"{class_name}.md"))

            elif fname.endswith(".py"):
                file_path = os.path.join(root, fname)
                module_name = fname[:-3]
                target_doc = os.path.abspath(
                    os.path.join(out_dir, f"{module_name}.md")
                )
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        py_source = f.read()
                    tree = ast.parse(py_source, filename=file_path)
                    class_names = [
                        node.name for node in tree.body if isinstance(node, ast.ClassDef)
                    ]
                    type_map[module_name] = target_doc
                    for class_name in class_names:
                        type_map[class_name] = target_doc
                except (IOError, UnicodeDecodeError, SyntaxError):
                    pass

    return type_map


def resolve_type_link(type_str: str, type_doc_map: dict, current_doc_dir: str, current_class: str = "") -> str:
    """Resolve a type string to a markdown link if documentation exists for it.
    
    Strips generics and array brackets to find the base type name.
    Returns the original type string wrapped in a link if found, otherwise returns it as-is in backticks.
    """
    # Extract the base type name (strip generics, arrays, wildcards)
    base_type = re.sub(r"<.*>", "", type_str)  # Remove generics
    base_type = re.sub(r"\[\]", "", base_type)  # Remove array brackets
    base_type = base_type.strip()

    # Don't link to self
    if base_type == current_class:
        return f"`{type_str}`"

    # Check if this type has documentation
    if base_type in type_doc_map:
        target_abs = type_doc_map[base_type]
        current_dir_abs = os.path.abspath(current_doc_dir)
        rel_path = os.path.relpath(target_abs, current_dir_abs).replace("\\", "/")
        return f"[`{type_str}`]({rel_path})"

    return f"`{type_str}`"


def linkify_inline_types(text: str, type_doc_map: dict, current_doc_dir: str, current_class: str = "") -> str:
    """Replace inline backtick-wrapped type references with links to their API docs.
    
    Matches `TypeName` in text (not already inside a markdown link) and replaces
    with [`TypeName`](path/to/TypeName.md) if documentation exists.
    """
    if not type_doc_map:
        return text

    def replace_backtick_ref(match):
        # Don't replace if already part of a link: [`Type`](...)
        # Check if preceded by [ 
        start = match.start()
        if start > 0 and text[start - 1] == "[":
            return match.group(0)

        type_name = match.group(1)
        # Extract base type (strip generics/arrays)
        base_type = re.sub(r"<.*>", "", type_name)
        base_type = re.sub(r"\[\]", "", base_type).strip()

        # Don't link to self
        if base_type == current_class:
            return match.group(0)

        # Check if this type has documentation
        if base_type in type_doc_map:
            target_abs = type_doc_map[base_type]
            current_dir_abs = os.path.abspath(current_doc_dir)
            rel_path = os.path.relpath(target_abs, current_dir_abs).replace("\\", "/")
            return f"[`{type_name}`]({rel_path})"

        return match.group(0)

    # Match `TypeName` but not already linked [`TypeName`](...)
    # Negative lookbehind for [ to avoid double-linking
    result = re.sub(r"(?<!\[)`([A-Z][\w<>\[\],\s]*?)`(?!\])", replace_backtick_ref, text)
    return result


def linkify_content(content: str, type_doc_map: dict, current_doc_dir: str, current_class: str = "") -> str:
    """Apply inline type linking to all lines in content, skipping code blocks."""
    lines = content.split("\n")
    result = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue

        if in_code_block:
            result.append(line)
        else:
            result.append(linkify_inline_types(line, type_doc_map, current_doc_dir, current_class))

    return "\n".join(result)


def compute_relative_source_path(
    source_file: str, source_root: str, doc_file_dir: str
) -> str:
    """Compute the relative path from the doc file to the source file."""
    source_abs = os.path.abspath(source_file)
    doc_dir_abs = os.path.abspath(doc_file_dir)

    return os.path.relpath(source_abs, doc_dir_abs).replace("\\", "/")


def build_api_header(class_info: JavaClassInfo, relative_source_path: str) -> List[str]:
    """Build the normalized header block for API docs."""
    sdd_filename = f"{class_info.name}_SDD.md"
    return [
        f"# {class_info.name}",
        "",
        f"> **Software Detailed Documentation:** [{sdd_filename}](./{sdd_filename})  ",
        f"> **Source File:** [{class_info.file_name}]({relative_source_path})",
        "",
    ]


def normalize_api_header(
    lines: List[str], class_info: JavaClassInfo, relative_source_path: str
) -> List[str]:
    """Replace the top title/header block in an API doc with the normalized format."""
    start = 0

    if lines and lines[0].startswith("# "):
        start = 1
        while start < len(lines) and not lines[start].strip():
            start += 1
        while start < len(lines) and lines[start].startswith("> "):
            start += 1
        while start < len(lines) and not lines[start].strip():
            start += 1

    return build_api_header(class_info, relative_source_path) + lines[start:]


def _extract_level2_section(lines: List[str], section_title: str) -> tuple:
    """Extract a level-2 section by title and return (section_lines, remaining_lines)."""
    start = -1
    for i, line in enumerate(lines):
        match = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if match and match.group(1).strip().lower() == section_title.lower():
            start = i
            break

    if start == -1:
        return [], lines[:]

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^##\s+", lines[i].strip()):
            end = i
            break

    return lines[start:end], lines[:start] + lines[end:]


def _trim_outer_blank_lines(lines: List[str]) -> List[str]:
    """Trim blank lines at the start and end of a line list."""
    result = lines[:]
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return result


def _heading_to_anchor(heading: str) -> str:
    """Convert a markdown heading text into a GitHub-style anchor."""
    anchor = heading.strip().lower()
    anchor = anchor.replace("`", "")
    anchor = re.sub(r"[^\w\s-]", "", anchor)
    anchor = re.sub(r"\s+", "-", anchor)
    anchor = re.sub(r"-+", "-", anchor).strip("-")
    return anchor


def _build_toc_section(lines: List[str], include_usage: bool = True) -> List[str]:
    """Build a Table of Contents section from level-2 headings in the document body."""
    entries = []
    seen = set()

    if include_usage:
        entries.append("- [Usage](#usage)")
        seen.add("usage")

    for line in lines:
        match = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if not match:
            continue
        heading = match.group(1).strip()
        if heading.lower() in ("table of contents", "usage"):
            continue
        anchor = _heading_to_anchor(heading)
        if not anchor or anchor in seen:
            continue
        entries.append(f"- [{heading}](#{anchor})")
        seen.add(anchor)

    return ["## Table of Contents", "", *entries, ""]


def _extract_header_block(lines: List[str]) -> tuple:
    """Extract markdown title + blockquote header block from the top of a doc."""
    if not lines:
        return [], []

    idx = 0
    header = []

    if lines[0].startswith("# "):
        header.append(lines[0])
        idx = 1

    while idx < len(lines) and not lines[idx].strip():
        header.append(lines[idx])
        idx += 1

    while idx < len(lines) and lines[idx].startswith("> "):
        header.append(lines[idx])
        idx += 1

    while idx < len(lines) and not lines[idx].strip():
        header.append(lines[idx])
        idx += 1

    return header, lines[idx:]


def _enforce_usage_and_toc_layout(
    lines: List[str],
    usage_placeholder: List[str],
) -> List[str]:
    """Ensure docs follow Header -> TOC -> Usage ordering and refresh TOC entries."""
    header, body = _extract_header_block(lines)

    usage_section, body = _extract_level2_section(body, "Usage")
    _toc_section, body = _extract_level2_section(body, "Table of Contents")

    usage_block = _trim_outer_blank_lines(usage_section) if usage_section else usage_placeholder[:]
    body = _trim_outer_blank_lines(body)

    rebuilt_toc = _build_toc_section(body, include_usage=True)

    result = []
    result.extend(header)
    if result and result[-1].strip():
        result.append("")

    result.extend(rebuilt_toc)
    result.append("")
    result.extend(usage_block)

    if body:
        result.append("")
        result.extend(body)

    while len(result) > 1 and not result[-1].strip() and not result[-2].strip():
        result.pop()

    return result


def _inject_api_method_descriptions(lines: List[str], class_info: JavaClassInfo) -> List[str]:
    """Replace default API TODO method descriptions with parsed docstrings/Javadocs."""
    method_map = {}
    for method in class_info.methods:
        heading = f"## {method.name} (Constructor)" if method.is_constructor else f"## {method.name}"
        method_map[heading] = method

    if not method_map:
        return lines

    updated = lines[:]
    i = 0
    while i < len(updated):
        if updated[i].startswith("## "):
            section_heading = updated[i].strip()
            method = method_map.get(section_heading)
            if method:
                section_end = len(updated)
                for j in range(i + 1, len(updated)):
                    if updated[j].startswith("## "):
                        section_end = j
                        break

                for j in range(i + 1, section_end):
                    if updated[j].strip() == "### Description":
                        k = j + 1
                        while k < section_end and not updated[k].strip():
                            k += 1
                        should_replace = False
                        if method.description and k < section_end:
                            if updated[k].strip().startswith("TODO: Describe what `"):
                                should_replace = True
                            else:
                                desc_block_end = section_end
                                for d in range(k, section_end):
                                    if updated[d].startswith("### "):
                                        desc_block_end = d
                                        break
                                current_desc = "\n".join(updated[k:desc_block_end])
                                if (
                                    "Arguments:" in current_desc
                                    or "Arguements:" in current_desc
                                    or "Returns:" in current_desc
                                ):
                                    should_replace = True

                        if should_replace:
                            replacement = method.description.strip().split("\n")
                            desc_block_end = section_end
                            for d in range(k, section_end):
                                if updated[d].startswith("### "):
                                    desc_block_end = d
                                    break
                            updated = updated[:k] + replacement + updated[desc_block_end:]

                        # Recompute section end after any edits above.
                        section_end = len(updated)
                        for d in range(i + 1, len(updated)):
                            if updated[d].startswith("## "):
                                section_end = d
                                break
                        break

                # Fill parameter description placeholders from doc metadata.
                for j in range(i + 1, section_end):
                    match = re.match(r"^\| `([^`]+)` \| (.+?) \| TODO: describe \|$", updated[j])
                    if not match:
                        continue
                    param_name = match.group(1)
                    param_type = match.group(2)
                    param_text = method.parameter_descriptions.get(param_name)
                    if param_text:
                        updated[j] = f"| `{param_name}` | {param_type} | {param_text} |"

                # Fill return placeholder if available.
                if method.return_description:
                    for j in range(i + 1, section_end):
                        if "— TODO: describe return value." in updated[j]:
                            updated[j] = updated[j].replace(
                                "— TODO: describe return value.",
                                f"— {method.return_description}",
                            )
                            break
        i += 1

    return updated


def _inject_sdd_method_descriptions(lines: List[str], class_info: JavaClassInfo) -> List[str]:
    """Replace default SDD TODO method descriptions with parsed docstrings/Javadocs."""
    method_to_description = {}
    constructor_description = None
    for method in class_info.methods:
        if not method.description:
            continue
        if method.is_constructor:
            constructor_description = method.description.strip()
        else:
            method_to_description[method.name] = method.description.strip()

    if not method_to_description and not constructor_description:
        return lines

    updated = lines[:]
    i = 0
    while i < len(updated):
        heading_match = re.match(r"^##\s+\d+\.\s+(.+?)\s*$", updated[i].strip())
        if not heading_match:
            i += 1
            continue

        label = heading_match.group(1).strip()
        description = None
        if label == "Constructor":
            description = constructor_description
        else:
            name_match = re.match(r"^`(\w+)\(\)`$", label)
            if name_match:
                description = method_to_description.get(name_match.group(1))

        if not description:
            i += 1
            continue

        section_end = len(updated)
        for j in range(i + 1, len(updated)):
            if updated[j].startswith("## "):
                section_end = j
                break

        for j in range(i + 1, section_end):
            if updated[j].strip().startswith("TODO: Provide detailed design explanation for `"):
                replacement = description.split("\n")
                updated = updated[:j] + replacement + updated[j + 1:]
                break

        i += 1

    return updated


# =============================================================================
# Merge Logic — update existing docs without losing manual content
# =============================================================================


def parse_existing_api_doc(file_path: str) -> dict:
    """Parse an existing API .md file and extract documented method names and structure.
    
    Returns a dict with:
      - 'content': full file content
      - 'documented_methods': set of method names found as ## headings
      - 'documented_fields': set of field names found in the Fields section
      - 'toc_end_line': line index where the Functions TOC ends
      - 'methods_start_line': line index where method sections begin (first ---)
      - 'see_also_line': line index of the See Also section (or -1)
      - 'lines': list of all lines
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    documented_methods = set()
    documented_fields = set()
    toc_end_line = -1
    methods_start_line = -1
    see_also_line = -1
    in_fields = False
    in_toc = False

    for i, line in enumerate(lines):
        # Detect fields section
        if line.startswith("**Fields:**") or line.strip() == "## Fields":
            in_fields = True
            continue
        if in_fields:
            field_match = re.match(r"^- `(\w+)`", line)
            if field_match:
                documented_fields.add(field_match.group(1))
            elif (not line.strip()) or line.startswith("## "):
                in_fields = False

        # Detect Functions TOC
        if line.startswith("**Functions:**"):
            in_toc = True
            continue
        if in_toc:
            if line.startswith("- ["):
                continue
            elif not line.strip():
                toc_end_line = i
                in_toc = False

        # Detect method sections (## headings)
        heading_match = re.match(r"^## (.+?)(?:\s*\(Constructor\))?\s*$", line)
        if heading_match:
            method_name = heading_match.group(1).strip()
            documented_methods.add(method_name)
            if methods_start_line == -1:
                # The --- before the first method section
                for j in range(i - 1, -1, -1):
                    if lines[j].strip() == "---":
                        methods_start_line = j
                        break
                if methods_start_line == -1:
                    methods_start_line = i

        # Detect See Also section
        if line.strip() == "## See Also":
            see_also_line = i
            # Also include the --- before it
            for j in range(i - 1, -1, -1):
                if lines[j].strip() == "---":
                    see_also_line = j
                    break

    return {
        "content": content,
        "documented_methods": documented_methods,
        "documented_fields": documented_fields,
        "toc_end_line": toc_end_line,
        "methods_start_line": methods_start_line,
        "see_also_line": see_also_line,
        "lines": lines,
    }


def parse_existing_sdd_doc(file_path: str) -> dict:
    """Parse an existing SDD _SDD.md file and extract documented method section names.
    
    Detects methods by:
      1. Numbered section headings like: ## 5. `methodName()`
      2. Method signatures in code blocks (handles methods grouped in a single section)
    
    Returns a dict with:
      - 'content': full file content
      - 'documented_methods': set of method names found
      - 'last_section_num': the highest section number found
      - 'lines': list of all lines
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    documented_methods = set()
    last_section_num = 0

    for line in lines:
        # Match sections like: ## 5. `methodName()`  or  ## 5. Constructor
        section_match = re.match(r"^## (\d+)\.\s+(?:`(\w+)\(\)`|Constructor)\s*$", line)
        if section_match:
            num = int(section_match.group(1))
            last_section_num = max(last_section_num, num)
            if section_match.group(2):
                documented_methods.add(section_match.group(2))
            else:
                documented_methods.add("__constructor__")
            continue

        # Match any numbered section heading (e.g., ## 7. Getter Methods)
        any_section_match = re.match(r"^## (\d+)\.", line)
        if any_section_match:
            num = int(any_section_match.group(1))
            last_section_num = max(last_section_num, num)

        # Also detect method signatures in code blocks to catch grouped methods
        # Matches: public ReturnType methodName(  or  private void methodName(
        sig_match = re.match(
            r"^(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>\[\],?\s]+?)\s+(\w+)\s*\(",
            line.strip(),
        )
        if sig_match:
            documented_methods.add(sig_match.group(1))

    return {
        "content": content,
        "documented_methods": documented_methods,
        "last_section_num": last_section_num,
        "lines": lines,
    }


def generate_api_method_section(method: MethodInfo, type_doc_map: dict, doc_dir: str, class_name: str, language: str = "java") -> str:
    """Generate a single method section for the API doc."""
    lines = []
    lang = "python" if language == "python" else "java"

    if method.is_constructor:
        lines.append(f"## {method.name} (Constructor)")
    else:
        lines.append(f"## {method.name}")
    lines.append("")

    lines.append("### Signature")
    lines.append("```" + lang)
    if method.annotations:
        for ann in method.annotations:
            lines.append(ann)
    lines.append(method.signature)
    lines.append("```")
    lines.append("")

    lines.append("### Description")
    if method.description:
        lines.append(method.description)
    else:
        lines.append(f"TODO: Describe what `{method.name}` does.")
    lines.append("")

    if method.parameters:
        lines.append("### Parameters")
        lines.append("| Name | Type | Description |")
        lines.append("|------|------|-------------|")
        for ptype, pname in method.parameters:
            type_link = resolve_type_link(ptype, type_doc_map, doc_dir, class_name)
            param_text = method.parameter_descriptions.get(pname, "TODO: describe")
            lines.append(f"| `{pname}` | {type_link} | {param_text} |")
        lines.append("")
    else:
        lines.append("### Parameters")
        lines.append("None.")
        lines.append("")

    lines.append("### Returns")
    if method.is_constructor:
        lines.append(f"`{method.name}` instance.")
    elif method.return_type == "void":
        lines.append("`void`")
    else:
        ret_link = resolve_type_link(method.return_type, type_doc_map, doc_dir, class_name)
        ret_text = method.return_description or "TODO: describe return value."
        lines.append(f"{ret_link} — {ret_text}")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_sdd_method_section(method: MethodInfo, section_num: int, language: str = "java") -> str:
    """Generate a single method section for the SDD doc."""
    lines = []
    lang = "python" if language == "python" else "java"

    if method.is_constructor:
        lines.append(f"## {section_num}. Constructor")
    else:
        lines.append(f"## {section_num}. `{method.name}()`")
    lines.append("")

    lines.append("```" + lang)
    if method.annotations:
        for ann in method.annotations:
            lines.append(ann)
    lines.append(method.signature)
    lines.append("```")
    lines.append("")
    if method.description:
        lines.append(method.description)
    else:
        lines.append(f"TODO: Provide detailed design explanation for `{method.name}`.")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def merge_api_doc(
    existing_path: str,
    class_info: JavaClassInfo,
    type_doc_map: dict,
    doc_dir: str,
    relative_source_path: str,
) -> str:
    """Merge new methods/fields into an existing API doc without removing existing content."""
    parsed = parse_existing_api_doc(existing_path)
    original_lines = parsed["lines"]
    original_text = parsed["content"]
    lines = normalize_api_header(original_lines, class_info, relative_source_path)

    new_fields = []
    new_methods = []

    # Find fields that are in source but not in the doc
    for f in class_info.fields:
        if f.name not in parsed["documented_fields"]:
            type_link = resolve_type_link(f.type, type_doc_map, doc_dir, class_info.name)
            new_fields.append(f"- `{f.name}` ({type_link}) — TODO: describe field")

    # Find methods that are in source but not in the doc
    for method in class_info.methods:
        method_doc_name = method.name
        if method_doc_name not in parsed["documented_methods"]:
            new_methods.append(method)

    if not new_fields and not new_methods:
        # Still check if See Also section needs to be moved to end
        see_also_found = False
        see_also_at_end = True
        for i, line in enumerate(lines):
            if re.match(r"^##\s+See Also", line):
                see_also_found = True
                # Check if there are any ## headings after this
                for j in range(i + 1, len(lines)):
                    if re.match(r"^## ", lines[j]) and not re.match(r"^##\s+See Also", lines[j]):
                        see_also_at_end = False
                        break
                break
        if see_also_found and not see_also_at_end:
            pass  # Fall through to the repositioning logic below
        else:
            lines = _inject_api_method_descriptions(lines, class_info)
            lines = _enforce_usage_and_toc_layout(
                lines,
                [
                    "## Usage",
                    "",
                    f"TODO: Add usage examples for `{class_info.name}`.",
                    "",
                ],
            )
            final_text = "\n".join(lines)
            return final_text if final_text != original_text else None

    # Insert new fields into the fields section
    if new_fields:
        # Find the end of the fields list (blank line after last field entry)
        fields_end = -1
        in_fields = False
        for i, line in enumerate(lines):
            if line.startswith("**Fields:**") or line.strip() == "## Fields":
                in_fields = True
                continue
            if in_fields:
                if re.match(r"^- `\w+`", line):
                    fields_end = i
                elif (not line.strip()) or line.startswith("## "):
                    break
        if fields_end >= 0:
            # Insert after the last field line
            for j, new_field in enumerate(new_fields):
                lines.insert(fields_end + 1 + j, new_field)

    # Insert new method sections before the See Also section (or at end)
    if new_methods:
        # Find and remove the See Also section so we can re-append it at the very end
        see_also_start = -1
        see_also_lines = []
        for i, line in enumerate(lines):
            if re.match(r"^##\s+See Also", line):
                # Find the start (include preceding --- if present)
                see_also_start = i
                for j in range(i - 1, -1, -1):
                    if lines[j].strip() == "---":
                        see_also_start = j
                        break
                    elif lines[j].strip():
                        break
                see_also_lines = lines[see_also_start:]
                lines = lines[:see_also_start]
                break

        # Remove trailing blank lines and separators before appending See Also
        while lines and not lines[-1].strip():
            lines.pop()
        # Remove trailing --- to avoid stacking separators
        while lines and lines[-1].strip() == "---":
            lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()
        lines.append("")

        # Append new method sections
        for method in new_methods:
            section = generate_api_method_section(method, type_doc_map, doc_dir, class_info.name, class_info.language)
            lines.extend(section.split("\n"))

        # Re-append See Also at the very end
        # Remove trailing blank/separator lines before See Also
        while lines and not lines[-1].strip():
            lines.pop()
        while lines and lines[-1].strip() == "---":
            lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()

        if see_also_lines:
            # Remove leading blank lines and separators from see_also
            while see_also_lines and not see_also_lines[0].strip():
                see_also_lines.pop(0)
            while see_also_lines and see_also_lines[0].strip() == "---":
                see_also_lines.pop(0)
            while see_also_lines and not see_also_lines[0].strip():
                see_also_lines.pop(0)
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.extend(see_also_lines)
        else:
            # Add a new See Also section if one didn't exist
            sdd_filename = f"{class_info.name}_SDD.md"
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("## See Also")
            lines.append("")
            lines.append(f"- **Software Detailed Design:** [{sdd_filename}](./{sdd_filename})")
            lines.append("")
    else:
        # Even if no new methods, ensure See Also is at end if it was misplaced
        see_also_start = -1
        see_also_lines = []
        for i, line in enumerate(lines):
            if re.match(r"^##\s+See Also", line):
                see_also_start = i
                for j in range(i - 1, -1, -1):
                    if lines[j].strip() == "---":
                        see_also_start = j
                        break
                    elif lines[j].strip():
                        break
                see_also_lines = lines[see_also_start:]
                lines = lines[:see_also_start]
                break

        if see_also_lines:
            # Re-append at end with clean separators
            while lines and not lines[-1].strip():
                lines.pop()
            while lines and lines[-1].strip() == "---":
                lines.pop()
            while lines and not lines[-1].strip():
                lines.pop()
            # Clean up see_also_lines
            while see_also_lines and not see_also_lines[0].strip():
                see_also_lines.pop(0)
            while see_also_lines and see_also_lines[0].strip() == "---":
                see_also_lines.pop(0)
            while see_also_lines and not see_also_lines[0].strip():
                see_also_lines.pop(0)
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.extend(see_also_lines)

    lines = _inject_api_method_descriptions(lines, class_info)

    lines = _enforce_usage_and_toc_layout(
        lines,
        [
            "## Usage",
            "",
            f"TODO: Add usage examples for `{class_info.name}`.",
            "",
        ],
    )

    final_text = "\n".join(lines)
    return final_text if final_text != original_text else None


def merge_sdd_doc(existing_path: str, class_info: JavaClassInfo) -> str:
    """Merge new method sections into an existing SDD doc without removing existing content."""
    parsed = parse_existing_sdd_doc(existing_path)
    lines = parsed["lines"]
    original_text = parsed["content"]

    new_methods = []
    for method in class_info.methods:
        lookup_name = "__constructor__" if method.is_constructor else method.name
        if lookup_name not in parsed["documented_methods"]:
            new_methods.append(method)

    if not new_methods:
        lines = _inject_sdd_method_descriptions(lines, class_info)
        lines = _enforce_usage_and_toc_layout(
            lines,
            [
                "## Usage",
                "",
                f"TODO: Describe how `{class_info.name}` is instantiated and used.",
                "",
            ],
        )
        final_text = "\n".join(lines)
        return final_text if final_text != original_text else None

    # Append new sections at the end of the file
    next_section_num = parsed["last_section_num"] + 1
    new_sections = []
    for method in new_methods:
        section = generate_sdd_method_section(method, next_section_num, class_info.language)
        new_sections.append(section)
        next_section_num += 1

    # Remove trailing blank lines and append
    while lines and not lines[-1].strip():
        lines.pop()

    lines.append("")
    for section in new_sections:
        lines.extend(section.split("\n"))

    lines = _inject_sdd_method_descriptions(lines, class_info)

    lines = _enforce_usage_and_toc_layout(
        lines,
        [
            "## Usage",
            "",
            f"TODO: Describe how `{class_info.name}` is instantiated and used.",
            "",
        ],
    )

    final_text = "\n".join(lines)
    return final_text if final_text != original_text else None


def generate_api_doc(
    class_info: JavaClassInfo, relative_source_path: str,
    type_doc_map: dict = None, doc_dir: str = ""
) -> str:
    """Generate the API documentation (.md) template."""
    if type_doc_map is None:
        type_doc_map = {}
    lines = build_api_header(class_info, relative_source_path)

    lines.append("## Table of Contents")
    lines.append("")
    lines.append("- [Usage](#usage)")
    if class_info.fields:
        lines.append("- [Fields](#fields)")
    if class_info.methods:
        seen_names = set()
        for m in class_info.methods:
            heading = m.name if not m.is_constructor else f"{m.name} (Constructor)"
            anchor = _heading_to_anchor(heading)
            if anchor not in seen_names:
                lines.append(f"- [{heading}](#{anchor})")
                seen_names.add(anchor)
    lines.append("- [See Also](#see-also)")
    lines.append("")

    lines.append("## Usage")
    lines.append("")
    lines.append(f"TODO: Add usage examples for `{class_info.name}`.")
    lines.append("")

    # Description placeholder
    if class_info.javadoc:
        lines.append(class_info.javadoc)
    else:
        lines.append(f"TODO: Add description for `{class_info.name}`.")
    lines.append("")

    # Constants section
    constants = [f for f in class_info.fields if f.is_static and f.is_final]
    non_constant_fields = [
        f for f in class_info.fields if not (f.is_static and f.is_final)
    ]
    if constants and non_constant_fields:
        # Already listed all above, no need to separate
        pass

    # Fields section
    if class_info.fields:
        lines.append("---")
        lines.append("")
        lines.append("## Fields")
        lines.append("")
        for f in class_info.fields:
            type_link = resolve_type_link(f.type, type_doc_map, doc_dir, class_info.name)
            lines.append(f"- `{f.name}` ({type_link}) — TODO: describe field")
        lines.append("")

    # Method details
    lang = "python" if class_info.language == "python" else "java"
    lines.append("---")
    lines.append("")

    for method in class_info.methods:
        if method.is_constructor:
            lines.append(f"## {method.name} (Constructor)")
        else:
            lines.append(f"## {method.name}")
        lines.append("")

        lines.append("### Signature")
        lines.append("```" + lang)
        if method.annotations:
            for ann in method.annotations:
                lines.append(ann)
        lines.append(method.signature)
        lines.append("```")
        lines.append("")

        lines.append("### Description")
        if method.description:
            lines.append(method.description)
        else:
            lines.append(f"TODO: Describe what `{method.name}` does.")
        lines.append("")

        if method.parameters:
            lines.append("### Parameters")
            lines.append("| Name | Type | Description |")
            lines.append("|------|------|-------------|")
            for ptype, pname in method.parameters:
                type_link = resolve_type_link(ptype, type_doc_map, doc_dir, class_info.name)
                param_text = method.parameter_descriptions.get(pname, "TODO: describe")
                lines.append(f"| `{pname}` | {type_link} | {param_text} |")
            lines.append("")
        else:
            lines.append("### Parameters")
            lines.append("None.")
            lines.append("")

        lines.append("### Returns")
        if method.is_constructor:
            lines.append(f"`{method.name}` instance.")
        elif method.return_type == "void":
            lines.append("`void`")
        else:
            ret_link = resolve_type_link(method.return_type, type_doc_map, doc_dir, class_info.name)
            ret_text = method.return_description or "TODO: describe return value."
            lines.append(f"{ret_link} — {ret_text}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # See Also section
    sdd_filename = f"{class_info.name}_SDD.md"
    lines.append("## See Also")
    lines.append("")
    lines.append(f"- **Software Detailed Design:** [{sdd_filename}](./{sdd_filename})")
    lines.append("")

    content = "\n".join(lines)
    return linkify_content(content, type_doc_map, doc_dir, class_info.name)


def generate_sdd_doc(
    class_info: JavaClassInfo,
    relative_source_path: str,
    api_doc_filename: str,
    type_doc_map: dict = None,
    doc_dir: str = "",
) -> str:
    """Generate the Software Detailed Design (_SDD.md) template."""
    if type_doc_map is None:
        type_doc_map = {}
    lines = []

    # Title
    lines.append(f"# {class_info.name} — Software Detailed Design")
    lines.append("")

    # Header links
    lines.append(f"> **API Documentation:** [{api_doc_filename}](./{api_doc_filename})  ")
    lines.append(
        f"> **Source File:** [{class_info.file_name}]({relative_source_path})"
    )
    lines.append("")

    toc_entries = [
        "- [Usage](#usage)",
        f"- [1. Overview](#{_heading_to_anchor('1. Overview')})",
    ]
    if class_info.language == "python":
        toc_entries.append(
            f"- [2. Module & Imports](#{_heading_to_anchor('2. Module & Imports')})"
        )
        toc_entries.append(
            f"- [3. Class Definition](#{_heading_to_anchor('3. Class Definition')})"
        )
    else:
        toc_entries.append(
            f"- [2. Package Declaration & Imports](#{_heading_to_anchor('2. Package Declaration & Imports')})"
        )
        toc_entries.append(
            f"- [3. Class Declaration](#{_heading_to_anchor('3. Class Declaration')})"
        )
    if class_info.fields:
        toc_entries.append(
            f"- [4. Instance Fields](#{_heading_to_anchor('4. Instance Fields')})"
        )

    section_num = 5 if class_info.fields else 4
    for method in class_info.methods:
        if method.is_constructor:
            heading = f"{section_num}. Constructor"
        else:
            heading = f"{section_num}. `{method.name}()`"
        toc_entries.append(f"- [{heading}](#{_heading_to_anchor(heading)})")
        section_num += 1

    lines.append("## Table of Contents")
    lines.append("")
    lines.extend(toc_entries)
    lines.append("")

    lines.append("## Usage")
    lines.append("")
    lines.append(f"TODO: Describe how `{class_info.name}` is instantiated and used.")
    lines.append("")

    lines.append("---")
    lines.append("")

    # Section 1: Overview
    lines.append("## 1. Overview")
    lines.append("")
    if class_info.javadoc:
        lines.append(class_info.javadoc)
    else:
        lines.append(f"TODO: Provide a high-level overview of `{class_info.name}`.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 2: Package / Module & Imports
    if class_info.language == "python":
        lines.append("## 2. Module & Imports")
        lines.append("")
        if class_info.imports:
            lines.append("```python")
            for imp in class_info.imports:
                if "." in imp:
                    parts = imp.rsplit(".", 1)
                    lines.append(f"from {parts[0]} import {parts[1]}")
                else:
                    lines.append(f"import {imp}")
            lines.append("```")
            lines.append("")
            lines.append("| Import | Purpose |")
            lines.append("|--------|---------|")
            for imp in class_info.imports:
                short_name = imp.split(".")[-1]
                lines.append(f"| `{short_name}` | TODO: describe purpose |")
            lines.append("")
    else:
        lines.append("## 2. Package Declaration & Imports")
        lines.append("")
        lines.append("```java")
        lines.append(f"package {class_info.package};")
        lines.append("```")
        lines.append("")

        if class_info.imports:
            lines.append("```java")
            for imp in class_info.imports:
                lines.append(f"import {imp};")
            lines.append("```")
            lines.append("")

            lines.append("| Import | Purpose |")
            lines.append("|--------|---------|")
            for imp in class_info.imports:
                short_name = imp.split(".")[-1]
                lines.append(f"| `{short_name}` | TODO: describe purpose |")
            lines.append("")

    lines.append("---")
    lines.append("")

    # Section 3: Class Declaration / Definition
    if class_info.language == "python":
        lines.append("## 3. Class Definition")
        lines.append("")
        lines.append("```python")
        lines.append(class_info.class_declaration)
        lines.append("```")
        lines.append("")
        if class_info.extends_class:
            lines.append(
                f"- **`{class_info.extends_class}`** — TODO: explain base class."
            )
        if class_info.implements:
            lines.append(
                f"- **`{', '.join(class_info.implements)}`** — TODO: explain other base classes."
            )
    else:
        lines.append("## 3. Class Declaration")
        lines.append("")
        lines.append("```java")
        lines.append(class_info.class_declaration)
        lines.append("```")
        lines.append("")
        if class_info.extends_class:
            lines.append(
                f"- **`extends {class_info.extends_class}`** — TODO: explain inheritance."
            )
        if class_info.implements:
            lines.append(
                f"- **`implements {', '.join(class_info.implements)}`** — TODO: explain interfaces."
            )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 4: Instance Fields
    section_num = 4
    if class_info.fields:
        lines.append(f"## {section_num}. Instance Fields")
        lines.append("")
        if class_info.language == "python":
            lines.append("```python")
            for f in class_info.fields:
                lines.append(f"{f.name}: {f.type}" if f.type else f.name)
            lines.append("```")
        else:
            lines.append("```java")
            for f in class_info.fields:
                static_str = "static " if f.is_static else ""
                final_str = "final " if f.is_final else ""
                lines.append(f"{f.access} {static_str}{final_str}{f.type} {f.name};")
            lines.append("```")
        lines.append("")

        lines.append("| Field | Type | Description |")
        lines.append("|-------|------|-------------|")
        for f in class_info.fields:
            lines.append(f"| `{f.name}` | `{f.type}` | TODO: describe |")
        lines.append("")
        lines.append("---")
        lines.append("")
        section_num += 1

    # Method sections
    lang = "python" if class_info.language == "python" else "java"
    for method in class_info.methods:
        if method.is_constructor:
            lines.append(f"## {section_num}. Constructor")
        else:
            lines.append(f"## {section_num}. `{method.name}()`")
        lines.append("")

        lines.append("```" + lang)
        if method.annotations:
            for ann in method.annotations:
                lines.append(ann)
        lines.append(method.signature)
        lines.append("```")
        lines.append("")
        if method.description:
            lines.append(method.description)
        else:
            lines.append(f"TODO: Provide detailed design explanation for `{method.name}`.")
        lines.append("")
        lines.append("---")
        lines.append("")
        section_num += 1

    content = "\n".join(lines)
    return linkify_content(content, type_doc_map, doc_dir, class_info.name)


def _process_class_info(
    class_info: JavaClassInfo,
    source_file: str,
    source_dir: str,
    doc_dir: str,
    docs_output_dir: str,
    type_doc_map: dict,
    overwrite: bool,
) -> tuple:
    """Generate or merge API and SDD docs for a single parsed class.

    Returns ``(generated, skipped)`` counts.
    """
    base_name = class_info.name
    api_doc_path = os.path.join(doc_dir, f"{base_name}.md")
    sdd_doc_path = os.path.join(doc_dir, f"{base_name}_SDD.md")
    relative_source = compute_relative_source_path(source_file, source_dir, doc_dir)

    api_exists = os.path.exists(api_doc_path)
    sdd_exists = os.path.exists(sdd_doc_path)

    if overwrite:
        api_content = generate_api_doc(class_info, relative_source, type_doc_map, doc_dir)
        with open(api_doc_path, "w", encoding="utf-8") as f:
            f.write(api_content)
        print(f"  CREATED: {os.path.relpath(api_doc_path, docs_output_dir)}")

        sdd_content = generate_sdd_doc(
            class_info, relative_source, f"{base_name}.md", type_doc_map, doc_dir
        )
        with open(sdd_doc_path, "w", encoding="utf-8") as f:
            f.write(sdd_content)
        print(f"  CREATED: {os.path.relpath(sdd_doc_path, docs_output_dir)}")
        return 1, 0

    elif api_exists and sdd_exists:
        merged_api = merge_api_doc(api_doc_path, class_info, type_doc_map, doc_dir, relative_source)
        merged_sdd = merge_sdd_doc(sdd_doc_path, class_info)

        if merged_api:
            merged_api = linkify_content(merged_api, type_doc_map, doc_dir, class_info.name)
            with open(api_doc_path, "w", encoding="utf-8") as f:
                f.write(merged_api)
            print(f"  MERGED:  {os.path.relpath(api_doc_path, docs_output_dir)}")
        else:
            with open(api_doc_path, "r", encoding="utf-8") as f:
                api_text = f.read()
            linked_api = linkify_content(api_text, type_doc_map, doc_dir, class_info.name)
            if linked_api != api_text:
                with open(api_doc_path, "w", encoding="utf-8") as f:
                    f.write(linked_api)

        if merged_sdd:
            merged_sdd = linkify_content(merged_sdd, type_doc_map, doc_dir, class_info.name)
            with open(sdd_doc_path, "w", encoding="utf-8") as f:
                f.write(merged_sdd)
            print(f"  MERGED:  {os.path.relpath(sdd_doc_path, docs_output_dir)}")
        else:
            with open(sdd_doc_path, "r", encoding="utf-8") as f:
                sdd_text = f.read()
            linked_sdd = linkify_content(sdd_text, type_doc_map, doc_dir, class_info.name)
            if linked_sdd != sdd_text:
                with open(sdd_doc_path, "w", encoding="utf-8") as f:
                    f.write(linked_sdd)

        if not merged_api and not merged_sdd:
            print(f"  UP-TO-DATE: {base_name}.md & {base_name}_SDD.md")
            return 0, 1
        return 1, 0

    else:
        if not api_exists:
            api_content = generate_api_doc(class_info, relative_source, type_doc_map, doc_dir)
            with open(api_doc_path, "w", encoding="utf-8") as f:
                f.write(api_content)
            print(f"  CREATED: {os.path.relpath(api_doc_path, docs_output_dir)}")

        if not sdd_exists:
            sdd_content = generate_sdd_doc(
                class_info, relative_source, f"{base_name}.md", type_doc_map, doc_dir
            )
            with open(sdd_doc_path, "w", encoding="utf-8") as f:
                f.write(sdd_content)
            print(f"  CREATED: {os.path.relpath(sdd_doc_path, docs_output_dir)}")
        return 1, 0


def generate_python_module_api_doc(
    module_info: PythonModuleDoc,
    relative_source_path: str,
    type_doc_map: dict = None,
    doc_dir: str = "",
) -> str:
    """Generate a module-level API documentation file for a Python source file."""
    if type_doc_map is None:
        type_doc_map = {}

    lines: List[str] = [
        f"# {module_info.module_name}",
        "",
        f"> **Software Detailed Documentation:** [{module_info.module_name}_SDD.md](./{module_info.module_name}_SDD.md)  ",
        f"> **Source File:** [{module_info.file_name}]({relative_source_path})",
        "",
    ]

    lines.append("## Table of Contents")
    lines.append("")
    lines.append("- [Usage](#usage)")
    if module_info.classes:
        lines.append("- [Classes](#classes)")
        for cls in module_info.classes:
            lines.append(f"- [Class `{cls.name}`](#class-{cls.name.lower()})")
    if module_info.functions:
        lines.append("- [Module Functions](#module-functions)")
    lines.append("- [See Also](#see-also)")
    lines.append("")

    lines.append("## Usage")
    lines.append("")
    lines.append(f"TODO: Add usage examples for `{module_info.module_name}`.")
    lines.append("")

    if module_info.module_docstring:
        lines.append(module_info.module_docstring)
    else:
        lines.append(f"TODO: Add module description for `{module_info.module_name}`.")
    lines.append("")

    if module_info.imports:
        lines.append("## Imports")
        lines.append("")
        for imp in module_info.imports:
            lines.append(f"- `{imp}`")
        lines.append("")

    if module_info.classes:
        lines.append("## Classes")
        lines.append("")
        for cls in module_info.classes:
            lines.append(f"### Class `{cls.name}`")
            lines.append("")
            lines.append("#### Declaration")
            lines.append("```python")
            lines.append(cls.class_declaration)
            lines.append("```")
            lines.append("")

            if cls.docstring:
                lines.append(cls.docstring)
            else:
                lines.append(f"TODO: Add description for class `{cls.name}`.")
            lines.append("")

            if cls.fields:
                lines.append("#### Fields")
                lines.append("")
                lines.append("| Name | Type | Description |")
                lines.append("|------|------|-------------|")
                for field in cls.fields:
                    field_type = field.type or "Any"
                    field_type_link = resolve_type_link(field_type, type_doc_map, doc_dir, cls.name)
                    lines.append(f"| `{field.name}` | {field_type_link} | TODO: describe field |")
                lines.append("")

            if cls.methods:
                lines.append("#### Methods")
                lines.append("")
                for method in cls.methods:
                    method_title = f"{cls.name}.{method.name}"
                    lines.append(f"##### {method_title}")
                    lines.append("")
                    lines.append("```python")
                    if method.annotations:
                        lines.extend(method.annotations)
                    lines.append(method.signature)
                    lines.append("```")
                    lines.append("")
                    lines.append(method.description or f"TODO: Describe what `{method_title}` does.")
                    lines.append("")

    if module_info.functions:
        lines.append("## Module Functions")
        lines.append("")
        for method in module_info.functions:
            lines.append(f"### {method.name}")
            lines.append("")
            lines.append("```python")
            if method.annotations:
                lines.extend(method.annotations)
            lines.append(method.signature)
            lines.append("```")
            lines.append("")
            lines.append(method.description or f"TODO: Describe what `{method.name}` does.")
            lines.append("")

    lines.append("## See Also")
    lines.append("")
    lines.append(f"- **Software Detailed Design:** [{module_info.module_name}_SDD.md](./{module_info.module_name}_SDD.md)")
    lines.append("")

    content = "\n".join(lines)
    return linkify_content(content, type_doc_map, doc_dir, module_info.module_name)


def generate_python_module_sdd_doc(
    module_info: PythonModuleDoc,
    relative_source_path: str,
    type_doc_map: dict = None,
    doc_dir: str = "",
) -> str:
    """Generate a module-level SDD file for a Python source file."""
    if type_doc_map is None:
        type_doc_map = {}

    lines: List[str] = [
        f"# {module_info.module_name} — Software Detailed Design",
        "",
        f"> **API Documentation:** [{module_info.module_name}.md](./{module_info.module_name}.md)  ",
        f"> **Source File:** [{module_info.file_name}]({relative_source_path})",
        "",
        "## Table of Contents",
        "",
        "- [Usage](#usage)",
        "- [1. Overview](#1-overview)",
        "- [2. Imports](#2-imports)",
    ]

    section_num = 3
    if module_info.classes:
        lines.append(f"- [{section_num}. Classes](#{section_num}-classes)")
        section_num += 1
    if module_info.functions:
        lines.append(f"- [{section_num}. Module-Level Functions](#{section_num}-module-level-functions)")
    lines.append("")

    lines.append("## Usage")
    lines.append("")
    lines.append(f"TODO: Describe how `{module_info.module_name}` is used.")
    lines.append("")

    lines.append("---")
    lines.append("")

    lines.append("## 1. Overview")
    lines.append("")
    lines.append(module_info.module_docstring or f"TODO: Provide an overview of `{module_info.module_name}`.")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 2. Imports")
    lines.append("")
    if module_info.imports:
        lines.append("```python")
        for imp in module_info.imports:
            if "." in imp:
                parts = imp.rsplit(".", 1)
                lines.append(f"from {parts[0]} import {parts[1]}")
            else:
                lines.append(f"import {imp}")
        lines.append("```")
    else:
        lines.append("No imports.")
    lines.append("")
    lines.append("---")
    lines.append("")

    next_section = 3
    if module_info.classes:
        lines.append(f"## {next_section}. Classes")
        lines.append("")
        for cls in module_info.classes:
            lines.append(f"### `{cls.name}`")
            lines.append("")
            lines.append("```python")
            lines.append(cls.class_declaration)
            lines.append("```")
            lines.append("")
            lines.append(cls.docstring or f"TODO: Explain class `{cls.name}`.")
            lines.append("")

            if cls.fields:
                lines.append("#### Fields")
                lines.append("")
                for fld in cls.fields:
                    lines.append(f"- `{fld.name}` (`{fld.type or 'Any'}`) — TODO: describe")
                lines.append("")

            if cls.methods:
                lines.append("#### Methods")
                lines.append("")
                for method in cls.methods:
                    lines.append("```python")
                    if method.annotations:
                        lines.extend(method.annotations)
                    lines.append(method.signature)
                    lines.append("```")
                    lines.append(method.description or f"TODO: Provide detailed design for `{cls.name}.{method.name}`.")
                    lines.append("")
        lines.append("---")
        lines.append("")
        next_section += 1

    if module_info.functions:
        lines.append(f"## {next_section}. Module-Level Functions")
        lines.append("")
        for method in module_info.functions:
            lines.append(f"### `{method.name}()`")
            lines.append("")
            lines.append("```python")
            if method.annotations:
                lines.extend(method.annotations)
            lines.append(method.signature)
            lines.append("```")
            lines.append(method.description or f"TODO: Provide detailed design for `{method.name}`.")
            lines.append("")

    content = "\n".join(lines)
    return linkify_content(content, type_doc_map, doc_dir, module_info.module_name)


def _process_python_module(
    module_info: PythonModuleDoc,
    source_file: str,
    source_dir: str,
    doc_dir: str,
    docs_output_dir: str,
    type_doc_map: dict,
    overwrite: bool,
) -> tuple:
    """Generate or refresh module-level docs for a Python source file."""
    base_name = module_info.module_name
    api_doc_path = os.path.join(doc_dir, f"{base_name}.md")
    sdd_doc_path = os.path.join(doc_dir, f"{base_name}_SDD.md")
    relative_source = compute_relative_source_path(source_file, source_dir, doc_dir)

    api_exists = os.path.exists(api_doc_path)
    sdd_exists = os.path.exists(sdd_doc_path)

    if overwrite or not api_exists:
        api_content = generate_python_module_api_doc(module_info, relative_source, type_doc_map, doc_dir)
        with open(api_doc_path, "w", encoding="utf-8") as f:
            f.write(api_content)
        print(f"  CREATED: {os.path.relpath(api_doc_path, docs_output_dir)}")

    if overwrite or not sdd_exists:
        sdd_content = generate_python_module_sdd_doc(module_info, relative_source, type_doc_map, doc_dir)
        with open(sdd_doc_path, "w", encoding="utf-8") as f:
            f.write(sdd_content)
        print(f"  CREATED: {os.path.relpath(sdd_doc_path, docs_output_dir)}")

    if overwrite or (not api_exists or not sdd_exists):
        return 1, 0

    # Existing module docs: normalize section placement (e.g., TOC before Usage)
    # and refresh TOC links even when no new source symbols were added.
    updated_any = False

    with open(api_doc_path, "r", encoding="utf-8") as f:
        api_lines = f.read().split("\n")
    normalized_api_lines = _enforce_usage_and_toc_layout(
        api_lines,
        [
            "## Usage",
            "",
            f"TODO: Add usage examples for `{module_info.module_name}`.",
            "",
        ],
    )
    normalized_api = "\n".join(normalized_api_lines)
    with open(api_doc_path, "r", encoding="utf-8") as f:
        existing_api = f.read()
    if normalized_api != existing_api:
        normalized_api = linkify_content(
            normalized_api,
            type_doc_map,
            doc_dir,
            module_info.module_name,
        )
        with open(api_doc_path, "w", encoding="utf-8") as f:
            f.write(normalized_api)
        print(f"  MERGED:  {os.path.relpath(api_doc_path, docs_output_dir)}")
        updated_any = True

    with open(sdd_doc_path, "r", encoding="utf-8") as f:
        sdd_lines = f.read().split("\n")
    normalized_sdd_lines = _enforce_usage_and_toc_layout(
        sdd_lines,
        [
            "## Usage",
            "",
            f"TODO: Describe how `{module_info.module_name}` is used.",
            "",
        ],
    )
    normalized_sdd = "\n".join(normalized_sdd_lines)
    with open(sdd_doc_path, "r", encoding="utf-8") as f:
        existing_sdd = f.read()
    if normalized_sdd != existing_sdd:
        normalized_sdd = linkify_content(
            normalized_sdd,
            type_doc_map,
            doc_dir,
            module_info.module_name,
        )
        with open(sdd_doc_path, "w", encoding="utf-8") as f:
            f.write(normalized_sdd)
        print(f"  MERGED:  {os.path.relpath(sdd_doc_path, docs_output_dir)}")
        updated_any = True

    if updated_any:
        return 1, 0

    print(f"  UP-TO-DATE: {base_name}.md & {base_name}_SDD.md")
    return 0, 1


def process_source_directory(
    source_dir: str, docs_output_dir: str, overwrite: bool = False
):
    """
    Walk the source directory and generate documentation templates.
    Supports Java (.java) and Python (.py) source files.
    """
    source_dir = os.path.abspath(source_dir)
    docs_output_dir = os.path.abspath(docs_output_dir)

    # Build type-to-doc-path mapping for cross-referencing
    type_doc_map = build_type_doc_map(source_dir, docs_output_dir)

    generated_count = 0
    skipped_count = 0

    for root, dirs, files in os.walk(source_dir):
        source_files = [f for f in files if f.endswith(".java") or f.endswith(".py")]
        if not source_files:
            continue

        # Compute relative path from source root
        rel_dir = os.path.relpath(root, source_dir)
        doc_dir = docs_output_dir if rel_dir == "." else os.path.join(docs_output_dir, rel_dir)

        # Create output directory
        os.makedirs(doc_dir, exist_ok=True)

        for fname in source_files:
            source_file = os.path.join(root, fname)

            if fname.endswith(".java"):
                class_info = parse_java_file(source_file)
                if not class_info:
                    print(f"  WARN: Could not parse {fname}")
                    continue
                infos = [class_info]
            else:  # .py
                module_info = parse_python_file(source_file)
                if not module_info:
                    print(f"  WARN: Could not parse {fname}")
                    continue
                gen, skip = _process_python_module(
                    module_info,
                    source_file,
                    source_dir,
                    doc_dir,
                    docs_output_dir,
                    type_doc_map,
                    overwrite,
                )
                generated_count += gen
                skipped_count += skip
                continue

            for class_info in infos:
                gen, skip = _process_class_info(
                    class_info, source_file, source_dir, doc_dir, docs_output_dir, type_doc_map, overwrite
                )
                generated_count += gen
                skipped_count += skip

    return generated_count, skipped_count

def main():
    """
    Entry point for the documentation generator script. Parses the command-line arguments and passes them forward to other functions.
    """
    parser = argparse.ArgumentParser(
        description="Generate documentation templates from Java and Python source files."
    )
    parser.add_argument(
        "source_dir",
        help="Path to the source code root directory (e.g., src/main/java/org/almond/buildinglore)",
    )
    parser.add_argument(
        "docs_output_dir",
        help="Path to the documentation output directory",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing documentation files (default: skip existing)",
    )

    args = parser.parse_args()

    # Validate paths
    if not os.path.isdir(args.source_dir):
        print(f"ERROR: Source directory not found: {args.source_dir}")
        sys.exit(1)

    print(f"Source directory: {os.path.abspath(args.source_dir)}")
    print(f"Output directory: {os.path.abspath(args.docs_output_dir)}")
    print(f"Overwrite mode:  {'ON' if args.overwrite else 'OFF'}")
    print()
    print("Generating documentation templates...")
    print("-" * 50)

    generated, skipped = process_source_directory(
        args.source_dir, args.docs_output_dir, args.overwrite
    )

    print("-" * 50)
    print(f"Done. Generated: {generated} file pairs, Skipped: {skipped} (already exist)")


if __name__ == "__main__":
    main()
