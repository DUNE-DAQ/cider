from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="cider",
    install_requires=[
        "textual",
        "textual_dev",
        "rich",
        "config-management @ git+ssh://git@gitlab.cern.ch:7999/dune-daq/online/config-management.git", # Config management
    ],
    extras_require={"develop": ["ipdb", "ipython"]},
    package_data={"": ["*.tcss", "*.yml"]},
)