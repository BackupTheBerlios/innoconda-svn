from twisted.trial import unittest
from twisted.python import util


import inno

class InnoTestCase(unittest.TestCase):
        
    def test_simple(self):
        inno.build(util.sibpath(__file__, 'data/simple.iss'))
