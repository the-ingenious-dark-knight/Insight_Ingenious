#!/usr/bin/env python
import os
import sys
import re

# require python 3.12 or newer
if sys.version_info < (3, 11):
    print("Error: This Generative AI Accelerator does not support this version of Python.")
    print("Please upgrade to Python 3.12 or higher.")
    sys.exit(1)

# require version of setuptools that supports find_namespace_packages
from setuptools import setup

try:
    from setuptools import find_namespace_packages
except ImportError:
    # the user has a downlevel version of setuptools.
    print("Error: This Generative AI  requires setuptools v40.1.0 or higher.")
    print('Please upgrade setuptools with "pip install --upgrade setuptools" ' "and try again")
    sys.exit(1)


# pull long description from README
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), "r", encoding="utf8") as f:
    long_description = f.read()

package_name = "ingenious"
package_version = "1.0.0"
print(f"printing version --------- {package_version}")
description = """A python library for accelerating Generative AI projects"""


INSTALL_REQUIRES = [
    "azure-core==1.31.0",
    "azure-search-documents==11.4.0",
    "azure-keyvault",
    "azure-identity",
    "certifi==2024.6.2",
    "chainlit==1.1.402",
    "chromadb==0.5.5",
    "Jinja2==3.1.4",
    "numpy==1.26.4",
    "openai==1.35.7",
    "pyautogen==0.2.35",
    "pydantic==2.8.0",
    "sentence-transformers==3.1.1",
    "markdownify==0.13.1",
    "pypdf==5.0.1",
    "IPython==8.28.0",
]


if sys.platform.startswith('win'):
    print("Windows detected")
    #INSTALL_REQUIRES.append("pywin32==3.0.6")

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="John Rampono, Elliot Zhu",
    author_email="john.rampono@insight.com, elliot.zhu@insight.com",
    url="https://github.com/Insight-Services-APAC/Insight_Ingenious",
    packages=find_namespace_packages(include=["ingenious"]),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "ingen_cli = ingenious.cli:app"
        ]
    }
)

