#from distutils.core import setup
from setuptools import setup, find_packages


#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["locator/*"]

setup(name = "locator",
    version = "0.2.2",
    description = "Simple gpo locator code parser",
    author = "Richard Larson",
    author_email = "rlarson@loc.gov",
    url = "www.loc.gov",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found
    #recursively.)
    packages = ['locator'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'package' : files },
    #'runner' is in the root.
    #scripts = ["runner"],
    long_description = """Ported the Thomas/LIS dailydigest parser code from C/ICON to simple python.""",
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []
    test_suite='nose.collector',
    tests_require=['nose']
)
