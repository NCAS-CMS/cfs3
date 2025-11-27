# -- PyData Sphinx Theme configuration for cfs3 -------------------------

import sys
from datetime import datetime
from pathlib import Path
import cfs3

# Make project root importable
root = Path(__file__).absolute().parent.parent
sys.path.insert(0, str(root))

# -----------------------------------------------------------------------------
# Basic project information
# -----------------------------------------------------------------------------

project = "cfs3"
author = "cfs3 Development Team"
copyright = f"{datetime.now().year}, cfs3 Development Team"

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

templates_path = ["_templates"]
exclude_patterns = []

# -----------------------------------------------------------------------------
# HTML output (replacing RTD theme with PyData theme)
# -----------------------------------------------------------------------------

html_theme = "pydata_sphinx_theme"

#html_logo = "figures/cfs3-logo.png"

html_theme_options = {
    "navigation_with_keys": True,
    "show_nav_level": 2,   # show some nested pages
    "secondary_sidebar_items": ["page-toc"],  # right-side table of contents
}

# Optional: override sidebar layout (usually not required)
html_sidebars = {
    "**": ["sidebar-nav-bs.html", "sidebar-ethical-ads.html"]
}

html_short_title = f"cfs3 {release}"
html_static_path = ["_static"]

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