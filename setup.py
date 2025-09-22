"""
Setup configuration for transistor-api package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="transistor-api",
    version="1.1.0",
    author="Amazon Q Developer",
    description="Complete Python client for Transistor.fm podcast hosting API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/transistor-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "transistor=transistor.cli:main",
        ],
    },
    keywords="transistor podcast api client hosting analytics",
    project_urls={
        "Bug Reports": "https://github.com/your-username/transistor-api/issues",
        "Source": "https://github.com/your-username/transistor-api",
        "Documentation": "https://developers.transistor.fm/",
    },
)
