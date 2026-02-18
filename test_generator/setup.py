from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="test-generator-multiagent",
    version="1.0.0",
    author="Gianmarco Riviello",
    description="Multi-agent system for automatic pytest test generation with 80%+ branch coverage using Google Gemini AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Core testing framework
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "coverage>=7.3.0",
        
        # LangChain ecosystem (Google Gemini integration)
        "langchain~=0.1.0",
        "langchain-google-genai>=0.0.6",
        "langchain-core~=0.1.0",
        "langgraph~=0.0.20",
        "pydantic>=2.5.0",
        
        # Code analysis
        "astroid>=3.0.0",
        "lark>=1.1.9",
        
        # Utilities
        "dataclasses-json>=0.6.0",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
        ],
    },
    include_package_data=True,
)
