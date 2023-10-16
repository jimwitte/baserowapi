#!/bin/bash
rm -rf dist build *.egg-info
python setup.py sdist bdist_wheel
