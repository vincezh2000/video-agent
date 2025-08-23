"""Setup configuration for Showrunner Agents system."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="showrunner-agents",
    version="0.1.0",
    author="Your Name",
    description="Multi-agent system for AI-driven TV episode generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "loguru>=0.7.0",
        "asyncio-mqtt>=0.16.0",
    ],
    entry_points={
        "console_scripts": [
            "showrunner=main:main",
        ],
    },
)