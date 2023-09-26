=========
Releasing
=========

These are the steps to create a release
=======================================

1.  Create Release branch::

    $ git checkout -b 0.7.x-release master

#.  Bump version number::

    $ poetry version 0.7.x

#.  Create a draft release in GitHub

    Generate the release notes in GitHub
    Add to the top of the CHANGELOG.rst file (TODO automate this step into the docs build)

#.  Test the build::

    $ poetry build

    Check the dist directory sources are as expected

#.  Commit changes and merge to master::

    $ git commit -m "Bump version to 0.7.x"

    Create and merge PR into master

#.  Publish the release on GitHub

    GitHub workflow `pythonpublish.yml` will then publish to pypi.org
    readthedocs will compile the latest docs

#.  Check the release

    Verify on pypi and readthedocs.io