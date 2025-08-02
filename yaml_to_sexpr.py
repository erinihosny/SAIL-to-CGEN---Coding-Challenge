#!/usr/bin/env python3
"""
yaml_to_sexpr.py

Reads YAML or JSON structured data and outputs an S-expression representation.

Enhanced Features:
- Scalars (strings, numbers, booleans, null)
- Nested mappings
- Lists (including nested)
- ISO date detection -> (make-date yyyy mm dd)
- Handles datetime.date (PyYAML auto-converts ISO dates)
- Multi-line text (quoted)
- Anchors & aliases resolved by PyYAML
- Multiple YAML documents (---)
- Environment variable substitution (optional)
- Preserves placeholders like {{ VAR }} (critical for SAIL → CGEN)
"""

import argparse
import json
import os
import re
import sys
import datetime
from pathlib import Path
import yaml


# ----------------------------
# Utility Functions
# ----------------------------

def substitute_env_variables(content: str) -> str:
    """Replace ${VAR_NAME} with environment values if enabled."""
    return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), content)


def load_data(input_file: Path, fmt: str = None, enable_env=False):
    """Load YAML or JSON data from a file, with optional env substitution."""
    with open(input_file, "r", encoding="utf-8") as f:
        raw = f.read()
        if enable_env:
            raw = substitute_env_variables(raw)
        if fmt == "yaml" or (fmt is None and input_file.suffix in [".yaml", ".yml"]):
            docs = list(yaml.safe_load_all(raw))
            return docs if len(docs) > 1 else docs[0]
        else:
            raise ValueError("Unsupported format or missing format flag.")


def is_iso_date(s: str) -> bool:
    """Check if string matches YYYY-MM-DD."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", s))


def escape_string(s: str) -> str:
    """Escape double quotes and backslashes for S-expression."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def is_symbolic_identifier(s: str) -> bool:
    # Symbol-like if it's a compact alphanumeric code (no spaces), has at least one digit, and no lowercase letters-only names
    return bool(re.match(r"^[A-Za-z0-9_]+$", s) and re.search(r"\d", s))


# ----------------------------
# Core Conversion Logic
# ----------------------------

def convert(obj, prefix="yaml", parent_key=None):
    """
    Recursively convert Python data to S-expression.
    - dict → nested (prefix:key ...)
    - list → (yaml:item ...)
    - date → (make-date yyyy mm dd)
    - strings → "quoted" or 'symbol if identifier
    """
    if isinstance(obj, dict):
        inner_parts = []
        for k, v in obj.items():
            inner_parts.append(f"({prefix}:{k} {convert(v, prefix, k)})")
        # Use newline for top-level
        separator = "\n" if parent_key is None else " "
        return separator.join(inner_parts)
    elif isinstance(obj, list):
        items = [f"({prefix}:item {convert(v, prefix)})" for v in obj]
        return f"(\n" + "\n".join(items) + ")"
    elif isinstance(obj, datetime.date):
        return f"(make-date {obj.year} {obj.month:02d} {obj.day:02d})"
    elif isinstance(obj, str):
        # Dates detected as strings
        if is_iso_date(obj):
            y, m, d = obj.split("-")
            return f"(make-date {y} {m} {d})"
        # Preserve placeholders
        if "{{" in obj and "}}" in obj:
            return f"\"{escape_string(obj)}\""
        # If it looks like an identifier (like A4786), quote it as symbol
        if is_symbolic_identifier(obj):
            return f"'{obj}"
        return f"\"{escape_string(obj)}\""
    elif obj is None:
        return "'nil"
    elif isinstance(obj, bool):
        return "#t" if obj else "#f"
    else:
        return str(obj)  # numeric or other scalars


# ----------------------------
# Pretty Printer
# ----------------------------

def format_sexpr(expr: str, indent=2):
    """Pretty-print S-expression with indentation, respecting explicit newlines."""
    result = []
    depth = 0
    token = ""
    for char in expr:
        if char == "(":
            if token.strip():
                result.append(token.strip())
                token = ""
            result.append("\n" + " " * (depth * indent) + "(")
            depth += 1
        elif char == ")":
            if token.strip():
                result.append(" " + token.strip())
                token = ""
            depth -= 1
            result.append(")")
        elif char == "\n":
            if token.strip():
                result.append(" " + token.strip())
                token = ""
            result.append("\n" + " " * (depth * indent))
        else:
            token += char
    return "".join(result).strip()


# ----------------------------
# Main CLI
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Convert YAML/JSON to S-expressions.")
    parser.add_argument("--input", "-i", required=True, help="Input file (.yaml or .json)")
    parser.add_argument("--output", "-o", help="Output file (optional)")
    parser.add_argument("--format", "-f", choices=["yaml", "json"], help="Input format")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print output")
    parser.add_argument("--env", action="store_true", help="Enable ${VAR} environment variable substitution")
    args = parser.parse_args()

    data = load_data(Path(args.input), args.format, enable_env=args.env)

    if isinstance(data, list) and all(isinstance(d, dict) for d in data):
        sexpr = f"({' '.join(['(' + convert(doc) + ')' for doc in data])})"
    else:
        sexpr = f"({convert(data)})"

    if args.pretty:
        sexpr = format_sexpr(sexpr)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out_f:
            out_f.write(sexpr)
    else:
        print(sexpr)


if __name__ == "__main__":
    main()
