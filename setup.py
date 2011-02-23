#!/usr/bin/env python
"""
Flask-OpenERP
-------------

This extension allows to use the OpenERP server with Flask

#!/usr/bin/env python
from flask import Flask
from flaskext.openerp import OpenERP

class DefaultConfig(object):
    OPENERP_PROTOCOL = 'netrpc'
    OPENERP_HOSTNAME = 'localhost'
    OPENERP_DATABASE = 'openerp'
    OPENERP_DEFAULT_USERNAME = 'admin'
    OPENERP_DEFAULT_PASSWORD = 'admin'
    OPENERP_PORT = 8070

    SECRET_KEY = 'secret_key'

    DEBUG = True

app = Flask(__name__)
app.config.from_object(DefaultConfig())
OpenERP(app)

@app.route('/')
def index():
    proxy = Object(g.openerp_cnx, 'res.users')
    users = proxy.select([], ['name', 'login'])

    return str(users)

app.run()
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
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
