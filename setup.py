# coding=utf-8
from setuptools import setup

setup(
    name = 'ring_doorbell',
    packages = ['ring_doorbell'],
    version = '0.0.1',
    description = 'A Python library to communicate with Ring Door Bell (https://ring.com/)',
    author = 'Marcelo Moreira de Mello',
    author_email = 'tchello.mello@gmail.com',
    url = 'https://github.com/tchellomello/python-ring_doorbell',
    license = 'LGPLv3+',
    include_package_data = True,
    keywords = [
        'ring',
        'door bell',
        'home automation',
        ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ' +
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)
