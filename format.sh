#!/bin/bash

# Format all python files
find . -type f -name "*.py" ! -path "*/.*" -exec isort {} \; -exec black {} \;