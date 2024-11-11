from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="llm-home-automation-analysis",  
    version="0.1.0", 
    author="Shreyas Rajesh, Chenda Duan",
    author_email="shreyasrajesh38@g.ucla.edu",
    description="This is the course project for ECE 202A, A comprehensive analysis of Local Large Language Models (LLMs) for home automation applications, focusing on performance tradeoffs across different model sizes and deployment strategies.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/shreyasrajesh0308/llm-home-automation-analysis", 
    # packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  # Specify your minimum Python version
    install_requires=[
        # List your package's dependencies here
        # e.g., 'requests>=2.24.0',
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
