#!/bin/bash
python -m build
copy /Y dist\*.whl E:\var\pypi
