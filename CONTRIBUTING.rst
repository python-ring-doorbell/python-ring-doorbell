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

Ready to contribute? Here's how to set up `python-ring_doorbell` for local development.

1. Fork the `python-ring-doorbel` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/python-ring-doorbell.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv python-ring-doorbell
    $ cd python-ring-doorbell/
    $ python setup.py develop
    $ pip install -r requirements_tests.txt

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ tox -r

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.


Thank you!!
