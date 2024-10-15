#!/bin/bash

# Set directories
docs="docs"
source="source"
demo_source="demos"
scripts="scripts"

source_dir="$docs/$source"
demo_cp="$source_dir/$demo_source"
scripts_dir="$docs/$scripts"

package="soupsavvy"

cp CONTRIBUTING.md $source_dir/contributing.md

# Copy demos to source/demos
rm -rf $demo_cp
cp -rf $demo_source $demo_cp

python $scripts_dir/update_index.py

sphinx-apidoc -o $source_dir $package --separate --force

python $scripts_dir/renaming.py $source_dir
python $scripts_dir/update_demos.py

cd docs
make clean && make html

rm $source/contributing.md
