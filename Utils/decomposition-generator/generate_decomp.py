"""
Decomposition Diagram Generator for Java Plugin Projects

Given a source code directory and documentation output folder, this script generates a decomposition diagram in PlantUML format for each java file. The diagrams show the dataflow for each file.

Usage:
    python generate_decomp.py <source_code_directory> <documentation_output_folder>

Example:
    python generate_decomp.py ../src/main/java/org/almond/buildinglore ../Documentation 
"""

import os
import sys
import re
from pathlib import Path
