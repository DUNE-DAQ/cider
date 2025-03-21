from setuptools import setup
import importlib

# Function to check if a package is installed
def is_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

# Determine the install_requires list based on whether config-management is installed
install_requires = [
    "textual",
    "textual_dev",
    "rich",
]


setup(
    name="cider",
    install_requires=install_requires,
    extras_require={"develop": ["ipdb", "ipython"],
                    "separate_conf": ["config_management @ git+https://gitlab.cern.ch/dune-daq/online/config-management.git"]},
    package_data={"": ["*.tcss", "*.yml"]},
)