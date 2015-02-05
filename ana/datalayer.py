import os
import weakref
import cPickle as pickle

import logging
l = logging.getLogger("ana.datalayer")

class DataLayer:
    '''
    The DataLayer handles storing and retrieving UUID-identified objects
    to/from a central store.
    '''

    def __init__(self, pickle_dir=None):
        self.uuid_cache = weakref.WeakValueDictionary()

        if pickle_dir is not None:
            l.debug("Pickling into directory.")

            self._store_type = 'pickle'
            self._dir = pickle_dir

            if not os.path.exists(self._dir):
                l.warning("Directory '%s' doesn't exit. Creating.", self._dir)
                os.makedirs(self._dir)
        else:
            l.debug("Pickling into dict.")

            self._store_type = 'dict'
            self._state_store = { }

    def store_state(self, uuid, s):
        p = pickle.dumps(s, protocol=pickle.HIGHEST_PROTOCOL)
        if len(p) == 0:
            raise Exception('wtf')
        if self._store_type == 'pickle':
            with open(os.path.join(self._dir, str(uuid)+'.p'), 'w') as f:
                f.write(p)
        elif self._store_type == 'dict':
            self._state_store[uuid] = p

    def load_state(self, uuid):
        if self._store_type == 'pickle':
            with open(os.path.join(self._dir, str(uuid)+'.p')) as f:
                p = f.read()
        elif self._store_type == 'dict':
            p = self._state_store[uuid]

        return pickle.loads(p)
