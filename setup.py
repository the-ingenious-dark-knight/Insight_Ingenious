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
    "aiofiles==23.2.1",
    "annotated-types==0.7.0",
    "anyio==3.7.1",
    "asgiref==3.8.1",
    "asyncer==0.0.2",
    "azure-common==1.1.28",
    "azure-core==1.30.2",
    "azure-cosmos==4.7.0",
    "azure-search-documents==11.4.0",
    "azure-keyvault",
    "azure-identity",
    "backoff==2.2.1",
    "bcrypt==4.2.0",
    "bidict==0.23.1",
    "build==1.2.1",
    "cachetools==5.5.0",
    "certifi==2024.6.2",
    "chainlit==1.1.402",
    "charset-normalizer==3.3.2",
    "chevron==0.14.0",
    "chroma-hnswlib==0.7.6",
    "chromadb==0.5.5",
    "click==8.1.7",
    "colorama==0.4.6",
    "coloredlogs==15.0.1",
    "colorlog==6.8.2",
    "dataclasses-json==0.5.14",
    "Deprecated==1.2.14",
    "diskcache==5.6.3",
    "distro==1.9.0",
    "dnspython==2.6.1",
    "docker==7.1.0",
    "email_validator==2.2.0",
    "exceptiongroup==1.2.1",
    "fastapi==0.110.3",
    "fastapi-cli==0.0.4",
    "filelock==3.15.4",
    "filetype==1.2.0",
    "FLAML==2.2.0",
    "flatbuffers==24.3.25",
    "fsspec==2024.6.1",
    "google-auth==2.34.0",
    "googleapis-common-protos==1.65.0",
    "grpcio==1.66.1",
    "h11==0.14.0",
    "httpcore==1.0.5",
    "httptools==0.6.1",
    "httpx==0.27.0",
    "huggingface-hub==0.24.6",
    "humanfriendly==10.0",
    "idna==3.7",
    "importlib_metadata==8.4.0",
    "importlib_resources==6.4.4",
    "isodate==0.6.1",
    "Jinja2==3.1.4",
    "kubernetes==30.1.0",
    "Lazify==0.4.0",
    "literalai==0.0.607",
    "markdown-it-py==3.0.0",
    "MarkupSafe==2.1.5",
    "marshmallow==3.22.0",
    "mdurl==0.1.2",
    "mmh3==4.1.0",
    "monotonic==1.6",
    "mpmath==1.3.0",
    "mypy-extensions==1.0.0",
    "nest-asyncio==1.6.0",
    "numpy==1.26.4",
    "oauthlib==3.2.2",
    "onnxruntime==1.19.0",
    "openai==1.35.7",
    "opentelemetry-api==1.27.0",
    "opentelemetry-exporter-otlp==1.27.0",
    "opentelemetry-exporter-otlp-proto-common==1.27.0",
    "opentelemetry-exporter-otlp-proto-grpc==1.27.0",
    "opentelemetry-exporter-otlp-proto-http==1.27.0",
    "opentelemetry-instrumentation==0.48b0",
    "opentelemetry-instrumentation-asgi==0.48b0",
    "opentelemetry-instrumentation-fastapi==0.48b0",
    "opentelemetry-instrumentation-httpx==0.48b0",
    "opentelemetry-proto==1.27.0",
    "opentelemetry-sdk==1.27.0",
    "opentelemetry-semantic-conventions==0.48b0",
    "opentelemetry-util-http==0.48b0",
    "orjson==3.10.5",
    "overrides==7.7.0",
    "packaging==23.2",
    "posthog==3.6.0",
    "protobuf==4.25.4",
    "pyasn1==0.6.0",
    "pyasn1_modules==0.4.0",
    "pyautogen==0.2.35",
    "pydantic==2.8.0",
    "pydantic-settings==2.3.4",
    "pydantic_core==2.20.0",
    "Pygments==2.18.0",
    "PyJWT==2.9.0",
    "PyPika==0.48.9",
    "pyproject_hooks==1.1.0",
    "pyreadline3==3.4.1",
    "python-dateutil==2.9.0.post0",
    "python-dotenv==1.0.1",
    "python-engineio==4.9.1",
    "python-multipart==0.0.9",
    "python-socketio==5.11.3",
    "PyYAML==6.0.1",
    "regex==2024.7.24",
    "requests==2.32.3",
    "requests-oauthlib==2.0.0",
    "rich==13.7.1",
    "rsa==4.9",
    "setuptools==74.0.0",
    "shellingham==1.5.4",
    "simple-websocket==1.0.0",
    "six==1.16.0",
    "sniffio==1.3.1",
    "starlette==0.37.2",
    "sympy==1.13.2",
    "syncer==2.0.3",
    "tenacity==9.0.0",
    "termcolor==2.4.0",
    "tiktoken==0.7.0",
    "tokenizers==0.20.0",
    "tomli==2.0.1",
    "tqdm==4.66.4",
    "typer==0.12.3",
    "typing-inspect==0.9.0",
    "typing_extensions==4.12.2",
    "ujson==5.10.0",
    "uptrace==1.26.0",
    "urllib3==2.2.2",
    "uvicorn==0.25.0",
    "watchfiles==0.20.0",
    "websocket-client==1.8.0",
    "websockets==12.0",
    "wrapt==1.16.0",
    "wsproto==1.2.0",
    "zipp==3.20.1",
    "markdownify==0.13.1",
    "pypdf==4.3.1",
    "ipython==8.27.0"
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

