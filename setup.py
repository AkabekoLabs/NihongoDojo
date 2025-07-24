"""
Setup configuration for Nihongo DoJo
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nihongo-dojo",
    version="1.0.0",
    author="Nihongo DoJo Team",
    author_email="contact@nihongo-dojo.com",
    description="A GRPO Dataset Library for Japanese Language Training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akabekolabs/nihongo-dojo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "tqdm>=4.60.0",
        "datasets>=2.0.0",
        "huggingface-hub>=0.10.0",
        "pandas>=1.3.0",
        "pyarrow>=5.0.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "japanize-matplotlib>=1.1.0",
        "transformers>=4.0.0",
        "torch>=1.9.0",
        "scikit-learn>=0.24.0",
        "regex>=2021.4.4",
        "requests>=2.25.0",
        "packaging>=20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "flake8>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nihongo-dojo=nihongo_dojo.code:main",
            "code=nihongo_dojo.code:main",
            "nihongo-dojo-generate=nihongo_dojo.generate_datasets:main",
            "nihongo-dojo-upload=nihongo_dojo.upload_to_huggingface:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nihongo_dojo": ["*.py"],
        "nihongo_dojo.data": ["*.py"],
        "nihongo_dojo.tasks": ["*.py"],
        "nihongo_dojo.kanji": ["*.py"],
    },
)