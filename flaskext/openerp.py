#!/usr/bin/env python
"""
    openerp.py
    ~~~~~~~~~~
    :copyright: (c) 2010-2011 Stephane Wirtel <stephane@wirtel.be>
    :license: LGPLv2
"""
from __future__ import absolute_import

from flask import _request_ctx_stack
from flask import session
from flask import g
from flask import abort

from .rpc import NetRPCConnector
from .rpc import XmlRPCConnector
from .rpc import Connection
from .rpc import Object
from .rpc import Common

__all__ = ['OpenERP', 'get_object', 'get_data_from_record', 'login']

def get_object(object_name):
    context = {
        'lang' :  g.user_language,
    }
    return Object(g.openerp_cnx, object_name, context)

def get_data_from_record(object_name, record_ids, fields=None):
    if fields is None:
        fields = []

    proxy = get_object(object_name)
    records = proxy.read(record_ids, fields)
    
    if records == False:
        abort(404)
        
    return records

class OpenERP(object):
    """
    This class is used to interact with an OpenERP Server to one or more Flask
    applications.
    
    There are two usage modes with work very similar. One is binding
    the instance to a very specific Flask application::

        app = Flask(__name__)
        openerp = OpenERP(app)
        
    The second possibility is to create the object once and configure
    the application later to support it::        
    
        openerp = OpenERP()
        
        def create_ap():
            app = Flask(__name__)
            openerp.init_app(app)
            return app
    """
    def __init__(self, app=None):
        self.default_user_id = None
        self.connector = None
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        """This callback can be used to initialize an application for use with
        the OpenERP server.
        """
        app.config.setdefault('OPENERP_PROTOCOL', 'netrpc')
        app.config.setdefault('OPENERP_PORT', 8070)
        app.config.setdefault('OPENERP_HOSTNAME', 'localhost')
        app.config.setdefault('OPENERP_DATABASE', 'openerp')
        app.config.setdefault('OPENERP_DEFAULT_USER', 'admin')
        app.config.setdefault('OPENERP_DEFAULT_PASSWORD', 'admin')

        app.jinja_env.globals.update(
            get_data_from_record=get_data_from_record
        )

        protocol = app.config['OPENERP_PROTOCOL'].lower()

        klass = {'netrpc' : NetRPCConnector,
                 'xmlrpc' : XmlRPCConnector}.get(protocol, False)

        if not klass:
            raise ValueError('This protocol is not handled by Flask-OpenERP')

        self.connector = klass(app.config['OPENERP_HOSTNAME'],
                               app.config['OPENERP_PORT'])

        cnx = Connection(self.connector,
                              app.config['OPENERP_DATABASE'],
                              app.config['OPENERP_DEFAULT_USER'],
                              app.config['OPENERP_DEFAULT_PASSWORD'])

        self.default_user_id = cnx.user_id

        app.before_request(self.before_request)

    def before_request(self):
        user_id = session.get('openerp_user_id', self.default_user_id) \
            or self.default_user_id

        password = session.get('openerp_password',
                               self.app.config['OPENERP_DEFAULT_PASSWORD']) \
            or self.app.config['OPENERP_DEFAULT_PASSWORD']

        g.openerp_cnx = Connection(self.connector,
                                   self.app.config['OPENERP_DATABASE'],
                                   user_id = user_id,
                                   password = password)

    def __repr__(self):
        app = None

        if self.app is not None:
            app = self.app
        else:
            ctx = _request_ctx_stack.top
            if ctx is not None:
                app = ctx.app
        return '<%s openerp=%r>' % (
            self.__class__.__name__,
            app and ("%s://%s:%d/%s" % (app.config['OPENERP_PROTOCOL'],
                                        app.config['OPENERP_HOSTNAME'],
                                        app.config['OPENERP_PORT'],
                                        app.config['OPENERP_DATABASE'])) or None
        )

    def login(self, username, password):
        return Common(self.connector).login(self.app.config['OPENERP_DATABASE'], username, password)


