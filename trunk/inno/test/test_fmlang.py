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
        self.fmp.replaceDuplicates = 1
        do = self.fmp.onecmd
        ckitems = lambda : zip(*self.fmp.data.items())[0]
        expected = (".\\'", # 0   "'" 
                    '.\\ x y z', # 1  " x y z"
                    '.\\LICENSE.inno', # 2 LICENSE.*
                    '.\\LICENSE.innoconda', # 3
                    '.\\LICENSE.process', # 4
                    '.\\actual.txt', # 5 *.txt
                    '.\\files.txt', # 6 
                    '.\\output.txt', # 7
                    '.\\THIRDPARTY.txt', # 8
                    '.\\TODO.txt', # 9
                    '.\\program\\', # 10 diradd program
                    '.\\fmlang.py', # 11  **/*.py*
                    '.\\fmlang.py~', # 12 
                    '.\\path.py', # 13
                    '.\\process.py', # 14
                    '.\\runner.py', # 15
                    '.\\script.py', # 16
                    '.\\version.py', # 17
                    '.\\__init__.py', # gets deleted!
                    '.\\test\\test_fmlang.py', # 18
                    '.\\test\\test_fmlang.py~', # 19
                    '.\\test\\test_inno.py', # 20
                    '.\\test\\__init__.py', # 21
                    '.\\test_fmlang.py', # 22 **/* (in test)
                    '.\\test_fmlang.py~', # 23
                    '.\\test_inno.py', # 24
                    '.\\__init__.py', # 25
                    '.\\CVS\\Entries', # 26
                    '.\\CVS\\Repository', # 27
                    '.\\CVS\\Root', # 28
                    '.\\data\\simple.iss', # 29
                    '.\\data\\CVS\\Entries', # 30
                    '.\\data\\CVS\\Repository', # 31
                    '.\\data\\CVS\\Root', # 32
                    '.\\Entries', # 33 **/* (in CVS)
                    '.\\Repository', # 34
                    '.\\Root', # 35
                    '.\\dir3\\1', # 36 **/* in dir, exclude dir2
                    '.\\dir2\\z') # 37 **/* in dir, include dir2
        do('exclude *.pyc')
        do('add "\'"')
        self.assertEqual(expected[:1], ckitems()[:1])
        do("add ' x y z' # spaces!")
        self.assertEqual(expected[1:2], ckitems()[1:2])
        do("exclude  *.pyo")
        do('chdir "%s" ' % os.getcwd())
        do("add LICENSE.* # woo licenses add stuff")
        self.assertEqual(expected[2:5], ckitems()[2:5])
        do("# comment ")
        do(" add *.txt")
        self.assertEqual(expected[5:10], ckitems()[5:10])
        do("  diradd program  ")
        self.assertEqual(expected[10:11], ckitems()[10:11])
        do("add **/*.py*")
        self.assertEqual(expected[11:23], ckitems()[11:23])
        do("chdir test")
        do("add **/*")
        # __init__ gets moved
        # because of replaceDuplicaties
        lex = list(expected)
        lex.remove('.\\__init__.py')
        expected = tuple(lex)
        self.assertEqual(expected[22:33], ckitems()[22:33])
        do("chdir ../CVS")
        do("add **/* # does this parse ok?")
        self.assertEqual(expected[33:36], ckitems()[33:36])
        do("chdir ../dir")
        do("exclude *dir2*")
        do("add **/*")
        self.assertEqual(expected[36:37], ckitems()[36:37])
        do("unexclude *dir2* ")
        do("exclude [xy]")
        do("add **/*")
        do("")
        do("# show")
        self.assertEqual(expected[37:38], ckitems()[37:38])
        self.assertEqual(expected, ckitems())

    def test_001invalidDir(self):
        self.fmp.replaceDuplicates = 0
        try:
            self.fmp.onecmd("cd foo")
        except InvalidDirectoryException:
            pass
        else:
            self.fail("\
Changing to invalid directory foo should have raised exception")
    def test_002duplicates(self):
        self.fmp.onecmd("cd '%s'/test" % os.getcwd())
        try:
            self.fmp.onecmd("add __init__.py")
        except DuplicateFileException:
            pass
        else:
            self.fail("\
Adding new __init__.py in no-replaceDuplicates mode did not raise exception")
    def test_003dirSelection(self):
        """Test that directories unadorned by / are treated like directories,
        and globs of directories work
        """
        fmp1 = FileMapperParser()
        fmp1.onecmd("chdir dir")
        fmp1.onecmd("add dir2/**/*")
        expected = ('.\\dir2\\x', '.\\dir2\\y', '.\\dir2\\z')
        actual = zip(*fmp1.data.items())[0]
        self.assertEqual(actual, expected)
        
        fmp2 = FileMapperParser()
        fmp2.onecmd("add dir/dir*/**/*")
        expected = ('.\\dir\\dir2\\x', '.\\dir\\dir2\\y', '.\\dir\\dir2\\z',
                    '.\\dir\\dir3\\1') 
        actual = zip(*fmp2.data.items())[0]
        self.assertEqual(actual, expected)
