# -- PyData Sphinx Theme configuration for cfs3 -------------------------

import sys
from datetime import datetime
from pathlib import Path
import cfs3

# Make project root importable
root = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(root))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

root = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(root))
exts = root/'doc/ext'
sys.path.insert(0, str(exts))


# -----------------------------------------------------------------------------
# Basic project information
# -----------------------------------------------------------------------------

project = "cfs3"
author = "Bryan Lawrence et al."
copyright = f"{datetime.now().year}, cfs3 contributors"

version = ".".join(cfs3.__version__.split(".")[0:1])
release = cfs3.__version__

master_doc = "index"
source_suffix = ".rst"

# -----------------------------------------------------------------------------
# Extensions
# -----------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "autodocsumm",
    "cmd2_formatter",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "inherited-members": True,
    "show-inheritance": True,
    "autosummary": True,
}

autodoc_mock_imports = [
    "cartopy", "cf_units", "ESMF", "geopy", "iris", "nested_lookup",
    "psutil", "stratify", "cf", "cfdm", "distributed"
]

templates_path = [str(Path(__file__).parent / "_templates")]
exclude_patterns = []

# -----------------------------------------------------------------------------
# HTML output (replacing RTD theme with PyData theme)
# -----------------------------------------------------------------------------

html_theme = "pydata_sphinx_theme"

#html_logo = "figures/cfs3-logo.png"

# Configure sidebars - hide left, show navigation on right
html_sidebars = {
    "**": []  # Hide left sidebar completely
}

html_theme_options = {
    # Navigation
    "navigation_with_keys": True,
    "navbar_align": "left",
    "show_prev_next": True,
    
    # Hide left sidebar
    "show_nav_level": 0,
    
    # Right sidebar - show page TOC
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    
    # Header - add navigation to top
    "navbar_end": ["navbar-icon-links", "theme-switcher"],
    "navbar_center": ["navbar-nav"],  # Shows main navigation in header
    
    # Footer
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version"],
}

html_title = f"cfs3 {release}"
html_short_title = f"cfs3 {release}"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -----------------------------------------------------------------------------
# Intersphinx cross-links
# -----------------------------------------------------------------------------

intersphinx_mapping = {
    "matplotlib": ("https://matplotlib.org/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "cf": ("https://ncas-cms.github.io/cf-python/", None),
}

# -----------------------------------------------------------------------------
# Numbering
# -----------------------------------------------------------------------------

numfig = True