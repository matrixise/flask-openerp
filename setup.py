#!/usr/bin/env python
"""
Flask-OpenERP
-------------

This extension allows to use the OpenERP server with Flask
"""

from setuptools import setup

setup(
    name='Flask-OpenERP',
    version='0.1',
    url='http://www.wirtel.be/projects/flask-openerp/',
    license='LGPLv2',
    author='Stephane Wirtel',
    author_email='stephane@wirtel.be',
    description='OpenERP Connector for Flask',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: LGPLv2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
