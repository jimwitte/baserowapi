from setuptools import setup, find_packages

setup(
    name="baserowapi",
    version="0.1.0b1",
    packages=find_packages(),
    install_requires=[
        "pytz>=2023.3.post1",
        "Requests~=2.31"
    ],
    author="James P Witte",
    author_email="jim@thunderingbison.com",
    description="API wrapper for Baserow", 
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",
    url="https://github.com/jimwitte/baserowapi",
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.10',
)
