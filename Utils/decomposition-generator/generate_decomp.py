"""
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
"""

import os
import sys
import re
import ast
from pathlib import Path


SUPPORTED_EXTENSIONS = {".java", ".py"}

JAVA_KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "new",
    "throw",
    "case",
    "do",
    "try",
    "else",
    "finally",
    "synchronized",
    "super",
    "this",
    "assert",
}

METHOD_MODIFIERS = {
    "public",
    "private",
    "protected",
    "static",
    "final",
    "abstract",
    "synchronized",
    "native",
    "strictfp",
    "default",
    "transient",
}

THEME_OPTIONS = {"light", "dark", "both", "none"}


def usage() -> None:
    """Print usage information for the script."""
    print(
        "Usage: python generate_decomp.py <source_code_directory> <documentation_output_folder> [theme] [verbose]"
    )
    print("Theme: light | dark | both | none (default: both)")
    print("Verbose: include all calls, including library/import calls")


def collect_source_files(source_root: Path) -> list[Path]:
    """Collect all supported source files from the given source root directory.
    
    Arguments:
        source_root: The root directory to search for source files.
        
    Returns:
        A sorted list of Path objects representing source files found.
    """
    source_files: list[Path] = []
    for root, _, files in os.walk(source_root):
        for filename in files:
            candidate = Path(root) / filename
            if candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                source_files.append(candidate)
    source_files.sort()
    return source_files


def strip_comments_and_strings(code: str) -> str:
    """Strip comments and string literals from Java source code while preserving character positions.
    
    Arguments:
        code: The Java source code as a string.
    
    Returns:
        The code with comments and string literals replaced by spaces.
    """
    # Preserve character positions by replacing comments and strings with spaces.
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub(lambda m: " " * len(m.group(0)), code)


def find_matching_brace(text: str, open_brace_idx: int) -> int:
    """Find the index of the matching closing brace for the opening brace at the given index.
    
    Arguments:
        text: The text to search within.
        open_brace_idx: The index of the opening brace '{'.
    
    Returns:
        The index of the matching closing brace '}', or -1 if not found.
    """
    depth = 0
    for idx in range(open_brace_idx, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return idx
    return -1


def class_names(code: str) -> set[str]:
    """Extract class, enum, and record names from Java source code.
    
    Arguments:
        code: The Java source code as a string.
    
    Returns:
        A set of class, enum, and record names defined in the code.
    """
    names = set()
    for match in re.finditer(r"\bclass\s+([A-Za-z_]\w*)", code):
        names.add(match.group(1))
    for match in re.finditer(r"\benum\s+([A-Za-z_]\w*)", code):
        names.add(match.group(1))
    for match in re.finditer(r"\brecord\s+([A-Za-z_]\w*)", code):
        names.add(match.group(1))
    return names


def is_probable_method_declaration(prefix: str, name: str, declared_types: set[str]) -> bool:
    """Determine if the given prefix and name likely represent a method declaration.
    
    Arguments:
        prefix: The code preceding the method name.
        name: The name of the method.
        declared_types: A set of declared class, enum, and record names.

    Returns:
        True if it is likely a method declaration, False otherwise.
    """
    if not prefix.strip():
        return False

    if name in JAVA_KEYWORDS:
        return False

    scrubbed = re.sub(r"@\w+(?:\([^()]*\))?", " ", prefix)
    words = re.findall(r"[A-Za-z_][\w$<>\[\].?]*", scrubbed)
    if not words:
        return False

    first = words[0]
    if first in {"new", "return", "throw", "case"}:
        return False

    has_non_modifier = any(word not in METHOD_MODIFIERS for word in words)
    if has_non_modifier:
        return True

    return name in declared_types


def extract_methods(cleaned_code: str) -> list[tuple[str, int, int]]:
    """Extract method declarations from cleaned Java source code.
    
    Arguments:
        cleaned_code: The Java source code with comments and strings stripped.
    
    Returns:
        A list of tuples containing the method name, start index, and end index.
    """
    types = class_names(cleaned_code)
    methods: list[tuple[str, int, int]] = []

    candidate_pattern = re.compile(
        r"([A-Za-z_]\w*)\s*\(([^;{}()]*)\)\s*(?:throws\s+[^{;]+)?\{",
        re.DOTALL,
    )

    for match in candidate_pattern.finditer(cleaned_code):
        name = match.group(1)
        open_brace_idx = match.end() - 1
        context_start = max(0, match.start() - 220)
        context = cleaned_code[context_start : match.start()]

        split_idx = max(context.rfind(";"), context.rfind("{"), context.rfind("}"))
        prefix = context[split_idx + 1 :] if split_idx != -1 else context

        if not is_probable_method_declaration(prefix, name, types):
            continue

        close_brace_idx = find_matching_brace(cleaned_code, open_brace_idx)
        if close_brace_idx == -1:
            continue

        methods.append((name, open_brace_idx + 1, close_brace_idx))

    return methods


def extract_calls(method_body: str) -> list[str]:
    """Extract method calls from a method body in Java source code.
    
    Arguments:
        method_body: The body of the method as a string.

    Returns:
        A list of method call names found in the method body.
    """
    calls: list[str] = []
    call_pattern = re.compile(r"(?:\b([A-Za-z_]\w*)\s*\.\s*)?([A-Za-z_]\w*)\s*\(")

    for match in call_pattern.finditer(method_body):
        callee = match.group(2)
        if callee in JAVA_KEYWORDS:
            continue
        if callee in {"class", "interface", "enum", "record"}:
            continue
        calls.append(callee)

    return calls


def has_java_value_return(method_body: str) -> bool:
    """Check whether a Java method body contains a return statement with a value.

    Arguments:
        method_body: The method body text (comments/strings already stripped).

    Returns:
        True when at least one `return <expr>;` is found, False otherwise.
    """
    for match in re.finditer(r"\breturn\b", method_body):
        idx = match.end()
        while idx < len(method_body) and method_body[idx].isspace():
            idx += 1
        if idx < len(method_body) and method_body[idx] != ";":
            return True
    return False


def attribute_chain_name(node: ast.AST) -> str | None:
    """Extract the full attribute chain name from an AST node.
    
    Arguments:
        node: An AST node representing a name or attribute.
    
    Returns:
        The full attribute chain name as a string, or None if not applicable.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = attribute_chain_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
        return node.attr
    return None


def simple_callable_name(node: ast.AST) -> str | None:
    """Extract the simple callable name from an AST node.
    
    Arguments:
        node: An AST node representing a name or attribute.
        
    Returns:
        The simple callable name as a string, or None if not applicable.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


class PythonMethodCallVisitor(ast.NodeVisitor):
    """AST visitor to collect method calls and local method definitions in Python code."""
    def __init__(self) -> None:
        """Initialize the visitor with empty structures for method calls and local methods."""
        self.method_calls: dict[str, list[str]] = {}
        self.local_methods: set[str] = set()
        self.returning_methods: set[str] = set()
        self._function_stack: list[str] = []
        self._class_stack: list[str] = []

    def current_function(self) -> str | None:
        """Get the name of the current function being visited, if any.

        Arguments:
            None
        
        Returns:
            The name of the current function as a string, or None if not inside a function.
        """
        if not self._function_stack:
            return None
        return self._function_stack[-1]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node and update the class stack.
        
        Arguments:
            node: An AST ClassDef node representing a class definition.
            
        Returns:
            None
        """
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node and process it for method calls.
        
        Arguments:
            node: An AST FunctionDef node representing a function definition.
            
        Returns:
            None
        """
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition node and process it for method calls.
        
        Arguments:
            node: An AST AsyncFunctionDef node representing an async function definition.
        
        Returns:
            None
        """
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Visit a function or async function definition node and process it for method calls.
        
        Arguments:
            node: An AST FunctionDef or AsyncFunctionDef node representing a function definition.
        
        Returns:
            None
        """
        if self._class_stack:
            qualified_name = f"{self._class_stack[-1]}.{node.name}"
        else:
            qualified_name = node.name

        self.local_methods.add(qualified_name)
        if self._function_has_value_return(node):
            self.returning_methods.add(qualified_name)
        self.method_calls.setdefault(qualified_name, [])
        self._function_stack.append(qualified_name)
        self.generic_visit(node)
        self._function_stack.pop()

    def _function_has_value_return(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Determine whether a function has at least one `return` with a value.

        This only inspects the current function body and intentionally skips nested
        function/class/lambda scopes.
        """

        class _ReturnValueVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.has_value = False

            def visit_Return(self, return_node: ast.Return) -> None:
                if return_node.value is not None:
                    self.has_value = True

            def visit_FunctionDef(self, _: ast.FunctionDef) -> None:
                return

            def visit_AsyncFunctionDef(self, _: ast.AsyncFunctionDef) -> None:
                return

            def visit_ClassDef(self, _: ast.ClassDef) -> None:
                return

            def visit_Lambda(self, _: ast.Lambda) -> None:
                return

        visitor = _ReturnValueVisitor()
        for statement in node.body:
            if visitor.has_value:
                break
            visitor.visit(statement)
        return visitor.has_value

    def visit_Call(self, node: ast.Call) -> None:
        """Visit a function call node and record the call if inside a function.
        
        Arguments:
            node: An AST Call node representing a function call.
            
        Returns:
            None
        """
        current = self.current_function()
        if current is not None:
            callee = simple_callable_name(node.func)
            if callee:
                self.method_calls.setdefault(current, []).append(callee)
        self.generic_visit(node)


def analyze_python_source(code: str) -> tuple[dict[str, list[str]], set[str], set[str]]:
    """Analyze Python source code to extract method calls and local method definitions.
    
    Arguments:
        code: The Python source code as a string.
    
    Returns:
        A tuple containing a dictionary of method calls, and a set of local method names.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}, set(), set()

    visitor = PythonMethodCallVisitor()
    visitor.visit(tree)
    return visitor.method_calls, visitor.local_methods, visitor.returning_methods


def analyze_java_source(code: str) -> tuple[dict[str, list[str]], set[str], set[str]]:
    """Analyze Java source code to extract method calls and local method definitions.

    Arguments:
        code: The Java source code as a string.

    Returns:
        A tuple containing a dictionary of method calls, and a set of local method names.
    """
    cleaned = strip_comments_and_strings(code)
    methods = extract_methods(cleaned)

    method_calls: dict[str, list[str]] = {}
    local_methods: set[str] = {method_name for method_name, _, _ in methods}
    returning_methods: set[str] = set()

    for method_name, body_start, body_end in methods:
        body = cleaned[body_start:body_end]
        calls = extract_calls(body)
        method_calls[method_name] = calls
        if has_java_value_return(body):
            returning_methods.add(method_name)

    return method_calls, local_methods, returning_methods


def sanitize_identifier(value: str) -> str:
    """Sanitize a string to be used as an identifier by replacing non-alphanumeric characters with underscores.
    
    Arguments:
        value: The string to sanitize.
        
    Returns:
        The sanitized string suitable for use as an identifier.
    """
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def simple_name(symbol: str) -> str:
    """Extract the simple name from a fully qualified symbol name.
    
    Arguments:
        symbol: The fully qualified symbol name (e.g., 'package.Class.method').
    
    Returns:
        The simple name (e.g., 'method').
    """
    return symbol.rsplit(".", 1)[-1]


def split_owner_and_method(symbol: str) -> tuple[str | None, str]:
    """Split a symbol into owner (e.g., class) and method name.

    Arguments:
        symbol: The symbol name, potentially qualified (e.g., 'Class.method').

    Returns:
        A tuple of (owner, method_name) where owner is None for unqualified symbols.
    """
    if "." not in symbol:
        return None, symbol

    owner, method = symbol.rsplit(".", 1)
    return owner, method


def filter_method_calls(
    method_calls: dict[str, list[str]],
    local_methods: set[str],
    global_project_callables: set[str],
    verbose: bool,
) -> dict[str, list[str]]:
    """Filter method calls to include only local and global project callables unless verbose is True.
    
    Arguments:
        method_calls: A dictionary mapping caller method names to lists of callee method names.
        local_methods: A set of local method names defined in the current file.
        global_project_callables: A set of global project callable names across all files.
        verbose: A boolean indicating whether to include all calls (True) or filter (False).
    
    Returns:
        A dictionary mapping caller method names to filtered lists of callee method names.
    """
    if verbose:
        return method_calls

    local_callable_names = {simple_name(name) for name in local_methods}
    filtered: dict[str, list[str]] = {}
    for caller, callees in method_calls.items():
        kept = [
            callee
            for callee in callees
            if callee in local_callable_names or callee in global_project_callables
        ]
        filtered[caller] = kept

    return filtered


def load_theme_lines(script_root: Path, theme: str) -> list[str]:
    """Load the PlantUML style lines for the specified theme.
    
    Arguments:
        script_root: The root directory of the script.
        theme: The name of the theme ('light', 'dark', or 'none').
    
    Returns:
        A list of lines from the theme's style file, excluding @startuml and @enduml.
    """
    if theme == "none":
        return []

    theme_map = {
        "light": script_root / "Light Theme" / "style.puml",
        "dark": script_root / "Dark Theme" / "style.puml",
    }

    style_file = theme_map.get(theme)
    if style_file is None or not style_file.exists():
        print(f"Theme file not found for '{theme}': {style_file}")
        return []

    raw_lines = style_file.read_text(encoding="utf-8", errors="replace").splitlines()
    cleaned_lines: list[str] = []
    for line in raw_lines:
        token = line.strip().lower()
        if token in {"@startuml", "@enduml"}:
            continue
        cleaned_lines.append(line)

    return cleaned_lines


def build_puml(
    relative_path: Path,
    method_calls: dict[str, list[str]],
    local_methods: set[str],
    returning_methods: set[str],
    theme_lines: list[str],
    theme_name: str,
) -> str:
    """Build the PlantUML diagram text for the given method calls and local methods.
    
    Arguments:
        relative_path: The relative path of the source file.
        method_calls: A dictionary mapping caller method names to lists of callee method names.
        local_methods: A set of local method names defined in the source file.
        theme_lines: A list of PlantUML style lines for the diagram.

    Returns:
        The PlantUML diagram text as a string.
    """
    lines: list[str] = []
    lines.append("@startuml")
    if theme_lines:
        lines.extend(theme_lines)
        lines.append("")
    if theme_name == "dark":
        file_bg, file_border = "#353b47", "#61afef"
        class_bg, class_border = "#424856", "#7db7ec"
        function_bg, function_border = "#4b5363", "#abb2bf"
    elif theme_name == "light":
        file_bg, file_border = "#dbeafe", "#2b6cb0"
        class_bg, class_border = "#eff6ff", "#5b7fb6"
        function_bg, function_border = "#f8fbff", "#6b8bbd"
    else:
        file_bg, file_border = "#e2e8f0", "#4a5568"
        class_bg, class_border = "#edf2f7", "#718096"
        function_bg, function_border = "#f7fafc", "#718096"

    lines.append("skinparam rectangle<<FileLevel>> {")
    lines.append(f"  BackgroundColor {file_bg}")
    lines.append(f"  BorderColor {file_border}")
    lines.append("  BorderThickness 2")
    lines.append("}")
    lines.append("skinparam rectangle<<ClassLevel>> {")
    lines.append(f"  BackgroundColor {class_bg}")
    lines.append(f"  BorderColor {class_border}")
    lines.append("  BorderThickness 1")
    lines.append("}")
    lines.append("skinparam component<<FunctionLevel>> {")
    lines.append(f"  BackgroundColor {function_bg}")
    lines.append(f"  BorderColor {function_border}")
    lines.append("  BorderThickness 1")
    lines.append("}")
    lines.append("")
    lines.append("hide stereotype")
    lines.append("left to right direction")
    lines.append(f"title Function Call Decomposition: {relative_path.as_posix()}")
    lines.append("skinparam packageStyle rectangle")
    lines.append("")

    file_label = relative_path.name
    file_alias = f"file_{sanitize_identifier(relative_path.stem)}"
    lines.append(f'rectangle "{file_label}" <<FileLevel>> as {file_alias} {{')

    method_alias: dict[str, str] = {}
    method_simple_alias: dict[str, str | None] = {}
    methods_by_owner: dict[str | None, list[str]] = {}
    for method_name in sorted(local_methods):
        owner, _ = split_owner_and_method(method_name)
        methods_by_owner.setdefault(owner, []).append(method_name)

    alias_counter = 1
    for owner in sorted(name for name in methods_by_owner if name is not None):
        class_alias = f"cls_{sanitize_identifier(owner)}"
        lines.append(f'  rectangle "{owner}" <<ClassLevel>> as {class_alias} {{')
        for method_name in methods_by_owner[owner]:
            _, method_base_name = split_owner_and_method(method_name)
            alias = f"m_{alias_counter}"
            alias_counter += 1
            method_alias[method_name] = alias
            if method_base_name in method_simple_alias:
                method_simple_alias[method_base_name] = None
            else:
                method_simple_alias[method_base_name] = alias
            lines.append(
                f'    component "{file_label}::<b>{method_name}()</b>" <<FunctionLevel>> as {alias}'
            )
        lines.append("  }")

    if None in methods_by_owner:
        global_alias = f"globals_{sanitize_identifier(relative_path.stem)}"
        lines.append(f'  rectangle "Top-Level Functions" <<ClassLevel>> as {global_alias} {{')
        for method_name in methods_by_owner[None]:
            _, method_base_name = split_owner_and_method(method_name)
            alias = f"m_{alias_counter}"
            alias_counter += 1
            method_alias[method_name] = alias
            if method_base_name in method_simple_alias:
                method_simple_alias[method_base_name] = None
            else:
                method_simple_alias[method_base_name] = alias
            lines.append(
                f'    component "{file_label}::<b>{method_name}()</b>" <<FunctionLevel>> as {alias}'
            )

        lines.append("  }")

    for method_name in sorted(local_methods):
        if method_name in method_alias:
            continue
        _, method_base_name = split_owner_and_method(method_name)
        alias = f"m_{alias_counter}"
        alias_counter += 1
        method_alias[method_name] = alias
        if method_base_name in method_simple_alias:
            method_simple_alias[method_base_name] = None
        else:
            method_simple_alias[method_base_name] = alias
        lines.append(
            f'  component "{file_label}::<b>{method_name}()</b>" <<FunctionLevel>> as {alias}'
        )

    lines.append("}")
    lines.append("")

    # Declare external callees before edges so PlantUML does not auto-create
    # placeholder elements that later conflict with explicit aliases.
    external_alias: dict[str, str] = {}
    for caller, callees in sorted(method_calls.items()):
        if caller not in method_alias:
            continue
        for callee in callees:
            is_local = callee in method_alias or method_simple_alias.get(callee) is not None
            if not is_local and callee not in external_alias:
                alias = f"ext_{len(external_alias) + 1}"
                external_alias[callee] = alias

    if external_alias:
        for callee, alias in sorted(external_alias.items()):
            lines.append(f'cloud "{callee}()" as {alias}')
        lines.append("")

    for caller, callees in sorted(method_calls.items()):
        if caller not in method_alias:
            continue
        caller_alias = method_alias[caller]
        emitted_targets: set[str] = set()
        for callee in callees:
            if callee in method_alias:
                callee_alias = method_alias[callee]
                if callee_alias in emitted_targets:
                    continue
                emitted_targets.add(callee_alias)
                arrow = "<-->" if callee in returning_methods else "-->"
                lines.append(f"{caller_alias} {arrow} {callee_alias}")
                continue

            local_alias = method_simple_alias.get(callee)
            if local_alias is not None:
                if local_alias in emitted_targets:
                    continue
                emitted_targets.add(local_alias)

                local_method_name: str | None = None
                for candidate_name, candidate_alias in method_alias.items():
                    if candidate_alias == local_alias:
                        local_method_name = candidate_name
                        break

                arrow = "<-->" if local_method_name in returning_methods else "-->"
                lines.append(f"{caller_alias} {arrow} {local_alias}")
            else:
                external_target = external_alias[callee]
                if external_target in emitted_targets:
                    continue
                emitted_targets.add(external_target)
                lines.append(f"{caller_alias} --> {external_target}")

    lines.append("@enduml")
    lines.append("")
    return "\n".join(lines)


def analyze_file(
    source_file: Path,
    source_root: Path,
) -> tuple[Path, dict[str, list[str]], set[str], set[str]]:
    """Analyze a source file to extract method calls and local method definitions.
    
    Arguments:
        source_file: The Path object representing the source file to analyze.
        source_root: The root directory of the source files.
    Returns:
        A tuple containing the relative path of the source file, a dictionary of method calls, and a set of local method definitions.
    """
    code = source_file.read_text(encoding="utf-8", errors="replace")
    suffix = source_file.suffix.lower()

    if suffix == ".java":
        method_calls, local_methods, returning_methods = analyze_java_source(code)
    elif suffix == ".py":
        method_calls, local_methods, returning_methods = analyze_python_source(code)
    else:
        method_calls, local_methods, returning_methods = {}, set(), set()

    relative_path = source_file.relative_to(source_root)
    return relative_path, method_calls, local_methods, returning_methods


def write_output(output_root: Path, relative_source: Path, diagram: str, suffix: str = "") -> Path:
    """Write the generated PlantUML diagram to the output directory.
    
    Arguments:
        output_root: The root directory for output files.
        relative_source: The relative path of the source file.
        diagram: The PlantUML diagram text to write.
        suffix: An optional suffix for the output file name.
    
    Returns:
        The Path object representing the written output file.
    """
    destination = output_root / relative_source.parent / f"{relative_source.stem}_decomposition{suffix}.puml"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(diagram, encoding="utf-8")
    return destination


def main() -> int:
    """Main function to process command-line arguments and generate decomposition diagrams.
    
    Returns:
        An integer exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < 3:
        usage()
        return 1

    source_root = Path(sys.argv[1]).resolve()
    output_root = Path(sys.argv[2]).resolve()
    theme_mode = "both"
    verbose = False
    theme_explicitly_set = False

    for arg in sys.argv[3:]:
        token = arg.lower()
        if token in THEME_OPTIONS:
            if theme_explicitly_set:
                print("Theme specified more than once.")
                usage()
                return 1
            theme_mode = token
            theme_explicitly_set = True
        elif token in {"verbose", "--verbose", "-v"}:
            verbose = True
        else:
            print(f"Invalid option '{arg}'.")
            usage()
            return 1

    if not source_root.exists() or not source_root.is_dir():
        print(f"Source directory not found: {source_root}")
        return 1

    output_root.mkdir(parents=True, exist_ok=True)
    source_files = collect_source_files(source_root)

    if not source_files:
        print(f"No supported source files found in: {source_root}")
        return 0

    file_analyses: list[tuple[Path, dict[str, list[str]], set[str], set[str]]] = []
    for source_file in source_files:
        file_analyses.append(analyze_file(source_file, source_root))

    global_project_callables: set[str] = set()
    for _, _, local_methods, _ in file_analyses:
        for local_method in local_methods:
            global_project_callables.add(simple_name(local_method))

    script_root = Path(__file__).resolve().parent
    theme_targets: list[tuple[str, str]]
    if theme_mode == "both":
        theme_targets = [("light", "_light"), ("dark", "_dark")]
    elif theme_mode == "none":
        theme_targets = [("none", "")]
    else:
        theme_targets = [(theme_mode, "")]

    generated = 0
    for theme_name, file_suffix in theme_targets:
        theme_lines = load_theme_lines(script_root, theme_name)
        for relative_source, method_calls, local_methods, returning_methods in file_analyses:
            filtered_calls = filter_method_calls(
                method_calls,
                local_methods,
                global_project_callables,
                verbose,
            )
            diagram = build_puml(
                relative_source,
                filtered_calls,
                local_methods,
                returning_methods,
                theme_lines,
                theme_name,
            )
            destination = write_output(output_root, relative_source, diagram, file_suffix)
            print(f"Generated ({theme_name}): {destination}")
            generated += 1

    print(f"Done. Generated {generated} decomposition diagrams.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
