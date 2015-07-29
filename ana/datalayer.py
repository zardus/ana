import os
import weakref
import cPickle as pickle

try:
    import pymongo
    import bson
except ImportError:
    # mongo dependency is optional
    pymongo = None

import logging
l = logging.getLogger("ana.datalayer")

class DataLayer:
    '''
    The DataLayer handles storing and retrieving UUID-identified objects
    to/from a central store.
    '''

    def __init__(self, pickle_dir=None, mongo_args=None, mongo_db='ana', mongo_collection='storage'):
        self.uuid_cache = weakref.WeakValueDictionary()

        if pickle_dir is not None:
            l.debug("Pickling into directory.")

            self._store_type = 'pickle'
            self._dir = pickle_dir

            if not os.path.exists(self._dir):
                l.warning("Directory '%s' doesn't exit. Creating.", self._dir)
                os.makedirs(self._dir)
        elif mongo_args is not None:
            if pymongo is None:
                raise ImportError("pymongo necessary for ANA mongo backend")

            l.debug("Pickling into mongo.")

            self._store_type = 'mongo'
            self._mongo = pymongo.MongoClient(*mongo_args)[mongo_db][mongo_collection]
        else:
            l.debug("Pickling into dict.")

            self._store_type = 'dict'
            self._state_store = { }

    def store_state(self, uuid, s):
        if self._store_type == 'pickle':
            with open(os.path.join(self._dir, str(uuid)+'.p'), 'w') as f:
                pickle.dump(s, f, protocol=pickle.HIGHEST_PROTOCOL)
        elif self._store_type == 'mongo':
            # TODO: investigate whether check/insert is faster than
            # upsert (because of latency) and also deal with the race
            # condition here
            if self._mongo.find({'_id': uuid}).limit(1).count(with_limit_and_skip=True) == 0:
                p = pickle.dumps(s, protocol=pickle.HIGHEST_PROTOCOL)
                self._mongo.insert_one({'_id': uuid, 'pickled': bson.binary.Binary(p)})
        elif self._store_type == 'dict':
            p = pickle.dumps(s, protocol=pickle.HIGHEST_PROTOCOL)
            self._state_store[uuid] = p

    def load_state(self, uuid):
        if self._store_type == 'pickle':
            with open(os.path.join(self._dir, str(uuid)+'.p')) as f:
                return pickle.load(f)
        elif self._store_type == 'mongo':
            p = self._mongo.find_one({'_id': uuid})['pickled']
        elif self._store_type == 'dict':
            p = self._state_store[uuid]

        return pickle.loads(p)
