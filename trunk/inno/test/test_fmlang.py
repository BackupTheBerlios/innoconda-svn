import os
from cStringIO import StringIO

from twisted.trial import unittest
from twisted.python import util
from twisted.python.zipstream import unzip

from inno.fmlang import FileMapperParser, DuplicateFileException, InvalidDirectoryException

class FMLangTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.fmp = FileMapperParser()
        
    def setUp(self):
        zipf = util.sibpath(__file__, "data/test_fmlang.zip")
        unzip(zipf, overwrite=1)
    def test_000collecting(self):
        scr = script_t % {'teststage': os.getcwd()}
        self.fmp.replaceDuplicates = 1
        for l in scr.split('\n'):
            self.fmp.onecmd(l)
        expected = (".\\'", '.\\ x y z', '.\\LICENSE.inno',
                    '.\\LICENSE.innoconda', '.\\LICENSE.process',
                    '.\\actual.txt', '.\\files.txt', '.\\output.txt',
                    '.\\THIRDPARTY.txt', '.\\TODO.txt', '.\\program\\',
                    '.\\fmlang.py', '.\\fmlang.py~', '.\\path.py',
                    '.\\process.py', '.\\runner.py', '.\\script.py',
                    '.\\test\\test_fmlang.py', '.\\test\\test_fmlang.py~',
                    '.\\test\\test_inno.py', '.\\test\\__init__.py',
                    '.\\version.py', '.\\CVS\\Entries', '.\\CVS\\Repository',
                    '.\\CVS\\Root', '.\\data\\CVS\\Entries',
                    '.\\data\\CVS\\Repository', '.\\data\\CVS\\Root',
                    '.\\data\\simple.iss', '.\\test_fmlang.py',
                    '.\\test_fmlang.py~', '.\\test_inno.py', '.\\__init__.py',
                    '.\\Entries', '.\\Repository', '.\\Root', '.\\dir2\\z')
        actual = zip(*self.fmp.data.items())[0]
        self.assertEqual(expected, actual)
    def test_001invalidDir(self):
        self.fmp.replaceDuplicates = 0
        try:
            self.fmp.onecmd("cd foo")
        except InvalidDirectoryException:
            pass
        else:
            self.fail("\
Changing to invalid directory foo should have raised Exception")
    def test_002duplicates(self):
        self.fmp.onecmd("cd ../test")
        try:
            self.fmp.onecmd("add __init__.py")
        except DuplicateFileException:
            pass
        else:
            self.fail("\
Adding new __init__.py in no-replaceDuplicates mode did not raise exception")
        


script_t = '''\
exclude *.pyc
add "\'"
add ' x y z' # spaces!
exclude  *.pyo
chdir "%(teststage)s"
add LICENSE.* # woo licenses add stuff
# comment
add *.txt
  diradd program
recurse *.py*
chdir test
recurse *
chdir ../CVS
recurse # does this parse ok?
chdir ../dir
exclude *dir2*
recurse
unexclude *dir2*
exclude [xy]
recurse
# show
'''
