============
Contributing
============

Contributions are welcome and very appreciated!!
Keep in mind that every little contribution helps, don't matter what.

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/python-ring-doorbell/python-ring-doorbell/issues

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

File an issue at https://github.com/python-ring-doorbell/python-ring-doorbell/issues.

Get Started!
------------

Ready to contribute? Here's how to set up `python-ring-doorbell` for local development.

1.  Fork the `python-ring-doorbell` repo on GitHub.

#.  Clone your fork locally::

    $ cd YOURDIRECTORYFORTHECODE
    $ git clone git@github.com:YOUR_GITHUB_USERNAME/python-ring-doorbell.git

#.  We are using `uv <https://docs.astral.sh/uv/>`_ for dependency management.

    If you dont have uv installed you can install it with::

    $ pipx install uv

    This installs uv in a virtual environment to isolate it from the rest of your system.  Then to install `python-ring-doorbell`::

    $ uv sync --all-extras

    uv will create a virtual environment for you and install all the requirements

#.  Create a branch for local development::

    $ git checkout -b NAME-OF-YOUR-BUGFIX-OR-FEATURE

    Now you can make your changes locally.

#.  To make sure your changes will pass the CI install pre-commit::

    $ pre-commit install

    You can check your changes prior to commit with::

    $ pre-commit run  # Runs against files added to staging
    $ pre-commit run --all-files # Runs against files not yet added to staging

#.  To test your changes::

    $ uv run pytest

#.  Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin NAME-OF-YOUR-BUGFIX-OR-FEATURE

#.  Submit a pull request through the GitHub website.

Thank you!!

Additional Notes
----------------

UV
~~~~~~

Dependencies
^^^^^^^^^^^^

uv is very useful at managing virtual environments and ensuring that dependencies all match up for you.
It manages this with the use of the `uv.lock` file which contains all the exact versions to be installed.
This means that if you add any dependecies you should do it via::

    $ uv add pypi_project_name

rather than pip.  This will update `pyproject.toml` and `uv.lock` accordingly.

To uninstall a dependency::

    $ uv remove pypi_project_name

finally if you want to add a dependency for development only::

    $ uv add --dev pypi_project_name

Environments
^^^^^^^^^^^^

uv creates a virtual environment for the project in the .venv directory.
You can activate the virtual environment with::

    $ source .venv/bin/activate

To exit the shell type ``deactivate``.
However you don't **need** to activate the virtual environment and you can run any command without activating it by::

    $ uv run SOME_COMMAND

See `uv <https://docs.astral.sh/uv/>`_ for more info

Documentation
^^^^^^^^^^^^^

To build the docs install with the docs extra::

    $ uv sync --extra docs

Then build::

    $ uv run make -C html
