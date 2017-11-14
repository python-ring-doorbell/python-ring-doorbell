# coding=utf-8
"""Python Ring Door Bell setup script."""
from setuptools import setup

setup(
    name='ring_doorbell',
    packages=['ring_doorbell'],
    version='0.1.7',
    description='A Python library to communicate with Ring' +
                ' Door Bell (https://ring.com/)',
    author='Marcelo Moreira de Mello',
    author_email='tchello.mello@gmail.com',
    url='https://github.com/tchellomello/python-ring-doorbell',
    license='LGPLv3+',
    include_package_data=True,
    install_requires=['requests', 'pytz'],
    test_suite='tests',
    keywords=[
        'ring',
        'door bell',
        'home automation',
        ],
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ' +
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)
