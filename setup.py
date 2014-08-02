#!/usr/bin/env python
"""
    setup.py
    ~~~~~~~~

    :copyright: 2011 - 2013 Stephane Wirtel <stephane@wirtel.be>
    :license: BSD
"""

from setuptools import setup

setup(
    name='Flask-OpenERP',
    version='0.3.1',
    url='https://github.com/matrixise/flask-openerp/',
    license='BSD',
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
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
