import os
import ana
import nose
import pickle

import logging
l = logging.getLogger("ana.test")

class A(ana.Storable):
    def __init__(self, n):
        self.n = n
        l.debug("Initialized %s", self)

    def __repr__(self):
        return "<A %d>" % self.n

    def _ana_getstate(self):
        return self.n

    def _ana_setstate(self, s):
        self.n = s

def test_ana():
    l.debug("Initializing 1")
    one = A(1)
    l.debug("Initializing 2")
    two = A(2)

    one.make_uuid()

    l.debug("Copying 1")
    one_p = pickle.dumps(one, pickle.HIGHEST_PROTOCOL)
    one_copy = pickle.loads(one_p)
    l.debug("Copying 2")
    two_p = pickle.dumps(two, pickle.HIGHEST_PROTOCOL)
    two_copy = pickle.loads(two_p)

    nose.tools.assert_is(one_copy, one)
    nose.tools.assert_is_not(two_copy, two)
    nose.tools.assert_equal(str(two_copy), str(two))

    nose.tools.assert_is(one, A.ana_load(one.ana_store()))
    nose.tools.assert_is(two, A.ana_load(two.ana_store()))

    two_copy2 = pickle.loads(pickle.dumps(two, pickle.HIGHEST_PROTOCOL))
    nose.tools.assert_equal(str(two_copy2), str(two))

def test_dir():
    ana.dl = ana.DataLayer(pickle_dir="/tmp/test_ana")
    one = A(1)
    nose.tools.assert_is(one, A.ana_load(one.ana_store()))
    nose.tools.assert_true(os.path.exists("/tmp/test_ana/%s.p" % one.ana_uuid))

if __name__ == '__main__':
    import sys
    logging.getLogger("ana.test").setLevel(logging.DEBUG)
    logging.getLogger("ana.storable").setLevel(logging.DEBUG)
    logging.getLogger("ana.datalayer").setLevel(logging.DEBUG)

    if len(sys.argv) > 1:
        getattr('test_%s' % sys.argv[1])()
    else:
        test_ana()
        test_dir()
