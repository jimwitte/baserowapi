import os
import sys
import sphinx_rtd_theme

# Point to the baserowapi directory, which is a sibling of the docsrc directory.
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
project = "Baserow API Package"
copyright = "2024, James P Witte"
author = "James P Witte"
release = "0.1.0b4"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
