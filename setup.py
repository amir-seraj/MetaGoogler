"""
Setup script for meta-googler package.
Provides backward compatibility with setup.py-based installations.
"""

from setuptools import setup, find_packages

setup(
    name="meta-googler",
    version="1.0.0",
    description="Song metadata management system with AI-powered suggestions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Amir Seraj",
    author_email="amir@example.com",
    url="https://github.com/amir-seraj/MetaGoogler",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "mutagen>=1.46.0",
        "librosa>=0.10.0",
        "numpy>=1.24.3",
        "scipy>=1.11.2",
        "customtkinter>=5.2.0",
        "requests>=2.31.0",
        "urllib3>=2.0.4",
        "litellm>=1.0.1",
        "python-dotenv>=1.0.0",
        "audioread>=3.1.1",
        "soundfile>=0.12.1",
        "Pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "meta-googler=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
