"""
Database connection for GAE. 

This mainly provides support for transactions.
"""
import logging

from django.db.backends import *
from django.db.backends.creation import BaseDatabaseCreation

from google.appengine.api.datastore import _GetConnection, _SetConnection

logger = logging.getLogger(__name__)

def complain(*args, **kwargs):
    pass

def ignore(*args, **kwargs):
    pass

class DatabaseError(Exception):
    pass

class IntegrityError(DatabaseError):
    pass

class DatabaseOperations(BaseDatabaseOperations):
    quote_name = complain

class DatabaseClient(BaseDatabaseClient):
    runshell = complain

class DatabaseIntrospection(BaseDatabaseIntrospection):
    get_table_list = complain
    get_table_description = complain
    get_relations = complain
    get_indexes = complain

class DatabaseWrapper(BaseDatabaseWrapper):
    
    close = ignore
    
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = BaseDatabaseFeatures(self)
        self.ops = DatabaseOperations()
        self.client = DatabaseClient(self)
        self.creation = BaseDatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)
        
        self.connection = None
        self.old_connection = None
        self.operators = []
    
    def _enter_transaction_management(self, managed):
        logger.info('Entering Transaction')
        self.managed(managed)
        self.old_connection = _GetConnection()
        # TODO: optionally pass a config 
        self.connection = self.old_connection.new_transaction()
        _SetConnection(self.connection)
    
    def _leave_transaction_management(self, managed):
        logger.info('Leaving Transaction')
        self.connection = self.old_connection
        _SetConnection(self.connection)
    
    def _commit(self):
        if hasattr(self.connection, 'commit'):
            self.connection.commit()
        else:
            logger.error("Not in transaction")
    
    def _rollback(self):
        logging.error('running rollback')
        if hasattr(self.connection, 'rollback'):
            self.connection.rollback()
        else:
            logger.error("Not in transaction")
