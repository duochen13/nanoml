"""Setup configuration for NanoRec package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version = {}
with open("nanorec/__version__.py") as f:
    exec(f.read(), version)

# Read long description (will create README.md later)
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else "NanoRec - Production ML Systems Made Easy"

setup(
    name="nanorec",
    version=version["__version__"],
    description="Production ML Recommendation Systems Made Easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NanoRec Team",
    author_email="team@nanorec.dev",
    url="https://github.com/nanorec/nanorec",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "nanorec": [
            "templates/**/*",
            "templates/**/**/*",
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
        "jsonschema>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nanorec=nanorec.cli.main:cli",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
