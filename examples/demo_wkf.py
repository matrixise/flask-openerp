#!/usr/bin/env python
"""
    demo.py
    ~~~~~~~

    :copyright: (c) 2011 - Stephane Wirtel <stephane@wirtel.be>
    :license: BSD License

"""
from flask import Flask
from flask import g
from flaskext.openerp import OpenERP, Object, Workflow

class DefaultConfig(object):
    OPENERP_PROTOCOL = 'xmlrpc'
    OPENERP_HOSTNAME = 'localhost'
    OPENERP_DATABASE = 'openrp'
    OPENERP_DEFAULT_USER = 'admin'
    OPENERP_DEFAULT_PASSWORD = 'admin'
    OPENERP_PORT = 8069

    SECRET_KEY = 'secret_key'

    DEBUG = True

app = Flask(__name__)
app.config.from_object(DefaultConfig())
OpenERP(app)

@app.route('/')
def index():

    wkf_service = Workflow(g.openerp_cnx)

    proxy = Object(g.openerp_cnx, 'sale.order')
    so_id = proxy.search([('state', '=', 'draft')], limit=1)
    
    wkf_service.execute_wkf('order_confirm', 'sale.order', so_id[0])    

    return ""

app.run()

