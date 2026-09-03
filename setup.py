from setuptools import setup, find_packages

setup(
    name="baserowapi",
    version="0.1.0b5",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "Requests~=2.31"
    ],
    author="James P Witte",
    author_email="jim@thunderingbison.com",
    description="API wrapper for Baserow", 
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",
    url="https://github.com/jimwitte/baserowapi",
    license="GPL-3.0-only",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires='>=3.12',
)
