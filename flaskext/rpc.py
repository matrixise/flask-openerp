#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2010-2011 Stephane Wirtel <stephane@wirtel.be>
    :license: LGPLv2

    Basic OpenObject Client Library over RPC
"""

import xmlrpclib
import logging
import socket
import sys
import time

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


# Safer Unpickler, in case the server is untrusted, from Nadia Alramli
# http://nadiana.com/python-pickle-insecure#How_to_Make_Unpickling_Safer
class SafeUnpickler(object):
    PICKLE_SAFE = {
        'exceptions': set(['Exception']),
    }

    @classmethod
    def find_class(cls, module, name):
        if not module in cls.PICKLE_SAFE:
            raise pickle.UnpicklingError(
                'Attempting to unpickle unsafe module %s' % module
            )
        __import__(module)
        mod = sys.modules[module]
        if not name in cls.PICKLE_SAFE[module]:
            raise pickle.UnpicklingError(
                'Attempting to unpickle unsafe class %s' % name
            )
        klass = getattr(mod, name)
        return klass

    @classmethod
    def loads(cls, pickle_string):
        pickle_obj = pickle.Unpickler(StringIO.StringIO(pickle_string))
        pickle_obj.find_global = cls.find_class
        return pickle_obj.load()



class Connector(object):
    """
    Connector class
    """

    __logger = logging.getLogger('connector')

    def __init__(self, hostname, port):
        """
        :param hostname: Host name of the server
        :param port: Port for the connection to the server
        """
        self.hostname = hostname
        self.port = port

class XmlRPCConnector(Connector):
    """
    This class supports the XmlRPC protocol
    """
    PROTOCOL = 'xmlrpc'

    def __init__(self, hostname, port=8069):
        Connector.__init__(self, hostname, port)
        self.__logger = logging.getLogger('connector.xmlrpc')
        self.url = 'http://%s:%d/xmlrpc' % (self.hostname, self.port)

    def send(self, service_name, method, *args):
        url = '%s/%s' % (self.url, service_name)
        service = xmlrpclib.ServerProxy(url)
        return getattr(service, method)(*args)

class NetRPC_Exception(Exception):
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString
        self.args = (faultCode, faultString)

class NetRPC:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.settimeout(120)
    def connect(self, host, port=False):
        if not port:
            protocol, buf = host.split('//')
            host, port = buf.split(':')
        self.sock.connect((host, int(port)))

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def mysend(self, msg, exception=False, traceback=None):
        msg = pickle.dumps([msg,traceback])
        size = len(msg)
        self.sock.send('%8d' % size)
        self.sock.send(exception and "1" or "0")
        totalsent = 0
        while totalsent < size:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError, "socket connection broken"
            totalsent = totalsent + sent

    def myreceive(self):
        buf=''
        while len(buf) < 8:
            chunk = self.sock.recv(8 - len(buf))
            if chunk == '':
                raise RuntimeError, "socket connection broken"
            buf += chunk
        size = int(buf)
        buf = self.sock.recv(1)
        if buf != "0":
            exception = buf
        else:
            exception = False
        msg = ''
        while len(msg) < size:
            chunk = self.sock.recv(size-len(msg))
            if chunk == '':
                raise RuntimeError, "socket connection broken"
            msg = msg + chunk
        res = SafeUnpickler.loads(msg)

        if isinstance(res[0],Exception):
            if exception:
                raise NetRPC_Exception(str(res[0]), str(res[1]))
            raise res[0]
        else:
            return res[0]

class NetRPCConnector(Connector):
    PROTOCOL = 'netrpc'

    def __init__(self, hostname, port=8070):
        Connector.__init__(self, hostname, port)
        self.__logger = logging.getLogger('connector.netrpc')

    def send(self, service_name, method, *args):
        socket = NetRPC()
        socket.connect(self.hostname, self.port)
        socket.mysend((service_name, method, )+args)
        result = socket.myreceive()
        socket.disconnect()
        return result

class Common(object):
    __logger = logging.getLogger('connection.common')

    def __init__(self, connector):
        self.connector = connector

    def __getattr__(self, method):
        """
        :param method: The method for the linked object (search, read, write, unlink, create, ...)
        """
        self.__logger.debug('method: %r', method)
        def proxy(*args):
            """
            :param args: A list of values for the method
            """
            self.__logger.debug('args: %r', args)
            result = self.connector.send('common', method, *args)
            self.__logger.debug('result: %r' % result)
            return result
        return proxy

class Database(object):
    __logger = logging.getLogger('connection.database')

    def __init__(self, connector):
        self.connector = connector

    def __getattr__(self, method):
        """
        :param method: The method for the linked object (search, read, write, unlink, create, ...)
        """
        #self.__logger.debug('method: %r', method)
        def proxy(*args):
            """
            :param args: A list of values for the method
            """
            self.__logger.debug('args: %r', args)
            result = self.connector.send('db', method, *args)
            self.__logger.debug('result: %r' % result)
            return result
        return proxy
    
class Connection(object):
    """
    TODO: Document this class
    """
    __logger = logging.getLogger('connection')

    def __init__(self, connector,
                 database,
                 login=None,
                 password=None,
                 user_id=None):
        """
        :param connector:
        :param database:
        :param login:
        :param password:
        """
        self.connector = connector
        self.database, self.login, self.password = database, login, password

        self.user_id = user_id
        if user_id is None:
            self.user_id = Common(self.connector).login(self.database, self.login, self.password)
            
        if self.user_id is False:
            raise Exception('The user can connect to the system !')
        self.__logger.debug(self.user_id)

    def __repr__(self):
        """
        Return a readable representation of the Connection object
        """
        url = "%(protocol)s://%(login)s:%(password)s@" \
              "%(hostname)s:%(port)d/%(database)s" % {
            'protocol' : self.connector.PROTOCOL,
            'login' : self.login,
            'password' : self.password,
            'hostname' : self.connector.hostname,
            'port' : self.connector.port,
            'database' : self.database,
        }
 
        return "Connection: %s" % url

class Object(object):
    """
    TODO: Document this class
    """
    __logger = logging.getLogger('object')

    def __repr__(self):
        """
        """
        return "Object <%s>" % (self.model)

    def __init__(self, connection, model, context=None):
        """
        :param connection:
        :param model:
        """
        self.connection = connection
        self.model = model

        self.context = context

    def __getattr__(self, method):
        """
        :param method: The method for the linked object (search, read, write, unlink, create, ...)
        """
        def proxy(*args):
            """
            :param args: A list of values for the method
            """
            return self.__send__(method, *args)
        return proxy

    def __send__(self, method, *args):
        self.__logger.debug('method: %r', method)
        self.__logger.debug('args: %r', args)
        result = self.connection.connector.send('object', 'execute',
                                                self.connection.database,
                                                self.connection.user_id,
                                                self.connection.password,
                                                self.model,
                                                method,
                                                *args)
        self.__logger.debug('result: %r', result)
        return result

    def __add_context(self, arguments, context=None):
        if context is None:
            context = {}

        if self.context is not None:
            context.update(self.context)

        arguments.append(context)
        return arguments

    def exists(self, oid, context=None):
        # TODO: Fucking bug, we can't use the read(fields=['id']), 
        # because the server returns a positive value but the record does not exist
        # into the database
        value = self.search_count([('id', '=', oid)], context=context)
        
        return value > 0
        
    def read(self, ids, fields=None, context=None):
        if fields is None:
            fields = []

        arguments = [ids, fields]
        arguments = self.__add_context(arguments, context)

        records = self.__send__('read', *arguments)

        if isinstance(ids, (list, tuple,)):
            records.sort(lambda x, y: cmp(ids.index(x['id']),
                                          ids.index(y['id'])))

        return records

    def search(self, domain=None, offset=0, limit=None, order=None, context=None):
        if domain is None:
            domain = []

        if limit is None:
            limit = self.search_count(domain)

        arguments = [domain, offset, limit, order is not None and order or False]

        arguments = self.__add_context(arguments, context)

        return self.__send__('search', *arguments)
        
    def search_count(self, domain, context=None):
        if context is None:
            context = {}
            
        return self.__send__('search_count', domain, context)

    def write(self, ids, values, context=None):
        if not isinstance(ids, (tuple, list)):
            ids = [ids]
        arguments = self.__add_context([ids, values], context)

        return self.__send__('write', *arguments)

    def create(self, values, context=None):
        arguments = self.__add_context([values], context)

        return self.__send__('create', *arguments)

    def unlink(self, ids, context=None):
        if not isinstance(ids, (tuple, list)):
            ids = [ids]
        arguments = self.__add_context([ids], context)

        return self.__send__('unlink', *arguments)

    def select(self, domain=None, fields=None, offset=0, limit=None, \
        order=None, context=None):
        
        record_ids = self.search(domain, offset=offset, limit=limit, \
                                 order=order, context=context)

        return self.read(record_ids, fields=fields, context=context)
