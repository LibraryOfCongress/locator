# locator

Locator is a python parser for GPO locator code (aka bell coded) printer files,
focused on html conversion.

## Installation

TODO: Describe the installation process
## Usage
Written for python3.

to run it:
    python locator.py  locator_file.rec  >locator_file.html >/dev/null

unit tests:
    python -m unittest discover

TODO: Write usage instructions

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

1.. Setup 2 factor auth if you have not done so already
2.  Generate personel token:
    https://help.github.com/articles/providing-your-2fa-authentication-code/
3.  setup caching of personal token for command line git so you do not have to keep looking up the token.
    https://help.github.com/articles/caching-your-github-password-in-git/

4.  Using the tutorial at 
    https://akrabat.com/the-beginners-guide-to-contributing-to-a-github-project/
    try cloning and modifying some files to get a handle on devloping
5. Clone the github project:
    git clone https://github.com/LibraryOfCongress/locator.git
6. Set the remote to be upstream so you can get updates:
    git remote add upstream  https://github.com/LibraryOfCongress/locator.git

    git checkout master
    git pull upstream master && git push origin master
    create a branch to do you work in: 
    git checkout -b feature/initial-update
7. Edit files.
8.  git push -u origin feature/initial-update 


## History

TODO: Write history

## Credits

Originally developed in the 90s as part of the thomas.loc.gov project using
C, Icon, shell and sed scripts.   Redeveloped in python and put on github as 
part of the congress.gov project.

## License

TODO: Write license
