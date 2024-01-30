============
Contributing
============

Contributions are welcome and very appreciated!!
Keep in mind that every little contribution helps, don't matter what.

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/tchellomello/python-ring-doorbell/issues

If you are reporting a bug, please include:

* Ring product and firmware version
* Steps to reproduce the issue
* Anything you judge interesting for the troubleshooting

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Documentation
~~~~~~~~~~~~~

Documentation is always good. So please feel free to add any documentation
you think will help our users.

Request Features
~~~~~~~~~~~~~~~~

File an issue at https://github.com/tchellomello/python-ring-doorbell/issues.

Get Started!
------------

Ready to contribute? Here's how to set up `python-ring-doorbell` for local development.

1.  Fork the `python-ring-doorbell` repo on GitHub.

#.  Clone your fork locally::

    $ cd YOURDIRECTORYFORTHECODE
    $ git clone git@github.com:YOUR_GITHUB_USERNAME/python-ring-doorbell.git

#.  We are using `poetry <https://python-poetry.org/>`_ for dependency management.

    If you dont have poetry installed you can install it with::
    
    $ curl -sSL https://install.python-poetry.org | python3 -

    This installs Poetry in a virtual environment to isolate it from the rest of your system.  Then to install `python-ring-doorbell`::

    $ poetry install

    Poetry will create a virtual environment for you and install all the requirements

    If you want to be able to build the docs (not necessary unless you are working on the doc generation)::

    $ poetry install --extras docs
    
#.  Create a branch for local development::

    $ git checkout -b NAME-OF-YOUR-BUGFIX-OR-FEATURE

    Now you can make your changes locally.

#.  We are using `tox <https://tox.wiki/>`_ for testing and linting::

    $ poetry run tox -r

#.  Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin NAME-OF-YOUR-BUGFIX-OR-FEATURE

#.  Submit a pull request through the GitHub website.

Thank you!!

Additional Notes
----------------

Poetry
~~~~~~

Dependencies
^^^^^^^^^^^^

Poetry is very useful at managing virtual environments and ensuring that dependencies all match up for you.  
It manages this with the use of the `poetry.lock` file which contains all the exact versions to be installed.
This means that if you add any dependecies you should do it via::

    $ poetry add pypi_project_name  

rather than pip.  This will update `pyproject.toml` and `poetry.lock` accordingly.  
If you install something in the virtual environment directly via pip you will need to run::

    $ poetry lock --no-update

to resync the lock file but without updating all the other requirements to latest versions.
To uninstall a dependency::

    $ poetry remove pypi_project_name

finally if you want to add a dependency for development only::

    $ poetry add --group dev pypi_project_name

Environments
^^^^^^^^^^^^

Poetry creates a virtual environment for the project and you can activate the virtual environment with::

    $ poetry shell

To exit the shell type ``exit`` rather than deactivate.
However you don't **need** to activate the virtual environment and you can run any command without activating it by::

    $ poetry run SOME_COMMAND

It is possible to manage all this from within a virtual environment you create yourself but that requires installing poetry
into the same virtual environment and this can potentially cause poetry to uninstall some of its own dependencies
in certain situations.  Hence the recommendation to install poetry into a seperate virtual environment of its via
the install script above or pipx.

See `poetry documentation <https://python-poetry.org/>`_ for more info

Documentation
^^^^^^^^^^^^^

To build the docs install with the docs extra::

    $ poetry install --extras docs

Then generate a `Github access token <https://github.com/settings/tokens/new?description=GitHub%20Changelog%20Generator%20token>`_
(no permissions are needed) and export it as follows::

    $ export CHANGELOG_GITHUB_TOKEN="«your-40-digit-github-token»"

Then build::

    $ make -C html

You can add the token to your shell profile to avoid having to export it each time. (e.g., .env, ~/.bash_profile, ~/.bashrc, ~/.zshrc, etc)