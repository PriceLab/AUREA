"""
Creates a proper MANIFEST

run with:

python build_Manifest.py > MANIFEST
"""
import os
print "README"
print "setup.py"
for root, _ , files in os.walk('src'):
    for file in files:
        print os.path.join(root,file)
