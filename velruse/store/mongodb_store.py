"""MongoDB UserStore implementation"""
try:
    import cPickle as pickle
except ImportError:
    import pickle


import pymongo
from pymongo import Connection
from pymongo.errors import ConnectionFailure
from pymongo.binary import Binary
from pymongo.errors import OperationFailure

from velruse.store.interface import UserStore
from velruse.utils import cached_property

class MongoDBStore(UserStore):
    """MongoDB Storage for Auth Provider"""
    def __init__(self, host='localhost', port=27017, db="mongo_db_name", collection='velruse_ustore'):
        self.host       = host
        self.port       = port
        self.db         = db
        self.collection = collection

    @classmethod
    def load_from_config(cls, config):
        """Load the MongoDBStore based on the config"""
        params = {}
        for k, v in config.items():
            key = k.lower()
            if key not in ['host', 'port', 'db', 'collection']:
                continue
            params[key] = v
        return cls(**params)

    @cached_property #Fix this later -htormey
    def _conn(self):
        """The MongoDB connection, cached for this call"""
        try:
            db_conn = Connection(self.host, self.port, slave_okay=False)
        except ConnectionFailure:
            raise Exception('Unable to connect to MongoDB')
        conn = db_conn[self.db]
        return conn

    def retrieve(self, key):
        data = self._conn[self.collection].find_one({'key' : key })
        if data:
            return pickle.loads(data['value'])
        else:
            return None

    def store(self, key, value, expires=None):
        try:
            r =  self._conn[self.collection].update({ 'key': key},
                { '$set' : { "value" : Binary(pickle.dumps(value)) }},
                upsert=True, safe=True)
        except OperationFailure:
            return False
        else:
            return True

    def delete(self, key):
        try:
            self._conn[self.collection].remove({'key' : key })
        except OperationFailure:
            return False
        else:
            return True

    def purge_expired(self):
        pass
