#!/bin/bash

# Set directories
demo_source="demos"
demo_cp="docs/source/demos"

docs="docs"
docs_source="docs/source"

package="soupsavvy"

# Copy demos to source/demos
rm -rf $demo_cp
cp -rf $demo_source $demo_cp

python $docs/update_index.py

sphinx-apidoc -o $docs_source $package --separate --force

python $docs/renaming.py $docs_source
python $docs/update_demos.py

cd docs
make clean && make html
