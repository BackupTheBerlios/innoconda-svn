from twisted.trial import unittest
from twisted.python import util, zipstream



import inno

class InnoTestCase(unittest.TestCase):
        
    def test_simple(self):
        inno.build(util.sibpath(__file__, 'data/simple.iss'))
    def test_complex(self):
        zf = util.sibpath(__file__, "data/test_fmlang.zip")
        zipstream.unzip(zf)
        scr = inno.Script()
        scr.collect('.')
        scr.compile()
