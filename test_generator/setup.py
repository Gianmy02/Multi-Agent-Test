from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="test-generator-multiagent",
    version="1.0.0",
    author="Multi-Agent System",
    description="Automatically generate pytest tests with 80+ branch coverage using AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/test-generator-multiagent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "coverage>=7.3.0",
    ],
    extras_require={
        "llm": [
            "openai>=1.3.0",
            "requests>=2.31.0",
        ],
        "dev": [
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "test-generator=test_generator.orchestrator:main",
        ],
    },
    include_package_data=True,
)
