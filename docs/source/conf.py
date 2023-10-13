import sphinx_rtd_theme
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------
project = 'Baserow API Package'
copyright = '2023, James P Witte'
author = 'James P Witte'
release = '0.1'

# -- General configuration ---------------------------------------------------
extensions = ['sphinx.ext.autodoc', 'sphinx_rtd_theme']

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
