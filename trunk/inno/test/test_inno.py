import sys
from cStringIO import StringIO

from twisted.trial import unittest
from twisted.python import util, zipstream

import inno

class InnoTestCase(unittest.TestCase):
    def test_simple(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        inno.build(util.sibpath(__file__, 'data/simple.iss'))
        sys.stdout = old_stdout
    def test_complex(self):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        zf = util.sibpath(__file__, "data/test_fmlang.zip")
        zipstream.unzip(zf)
        scr = inno.Script(name="complex", display_name="Complex Script",
                          package_version="1.1.1")
        scr.collect('.', exclude_globs=('test.log', ))
        scr.compile()
        sys.stdout = old_stdout
