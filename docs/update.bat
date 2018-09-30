cd C:\Users\patri_000\Git\nemoa
python setup.py install
cd docs
sphinx-apidoc -e -f -o C:\Users\patri_000\Git\nemoa\docs\source C:\Users\patri_000\Git\nemoa\lib\nemoa
make html