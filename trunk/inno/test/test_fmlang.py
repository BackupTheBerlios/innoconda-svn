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
        expected =(".\\'",
                   '.\\ x y z',
                   '.\\LICENSE.inno',
                   '.\\LICENSE.innoconda',
                   '.\\LICENSE.process',
                   '.\\actual.txt',
                   '.\\files.txt',
                   '.\\output.txt',
                   '.\\THIRDPARTY.txt',
                   '.\\TODO.txt',
                   '.\\program\\',
                   '.\\fmlang.py',
                   '.\\fmlang.py~',
                   '.\\path.py',
                   '.\\process.py',
                   '.\\runner.py',
                   '.\\script.py',
                   '.\\version.py',
                   '.\\__init__.py',
                   '.\\test\\test_fmlang.py',
                   '.\\test\\test_fmlang.py~',
                   '.\\test\\test_inno.py',
                   '.\\test\\__init__.py',
                   '.\\CVS\\Entries',
                   '.\\CVS\\Repository',
                   '.\\CVS\\Root',
                   '.\\data\\CVS\\Entries',
                   '.\\data\\CVS\\Repository',
                   '.\\data\\CVS\\Root',
                   '.\\data\\simple.iss',
                   '.\\test_fmlang.py',
                   '.\\test_fmlang.py~',
                   '.\\test_inno.py',
                   '.\\__init__.py',
                   '.\\Entries',
                   '.\\Repository',
                   '.\\Root',
                   '.\\dir3\\1',
                   '.\\dir2\\z')
        do('exclude *.pyc')
        do('add "\'"')
        self.assertEqual(expected[:1], ckitems())
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
        self.assertEqual(expected[11:22], ckitems()[11:22])
        do("chdir test")
        do("add **")
        self.assertEqual(expected[22:33], ckitems()[22:33])
        do("chdir ../CVS")
        do("add ** # does this parse ok?")
        self.assertEqual(expected[33:36], ckitems()[33:36])
        do("chdir ../dir")
        do("exclude *dir2*")
        do("add **")
        self.assertEqual(expected[36:37], ckitems()[36:37])
        do("unexclude *dir2* ")
        do("exclude [xy]")
        do("add **")
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
        fmp1.onecmd("add dir2/**")
        expected = ('.\\dir2\\x', '.\\dir2\\y', '.\\dir2\\z')
        actual = zip(*fmp1.data.items())[0]
        self.assertEqual(actual, expected)
        
        fmp2 = FileMapperParser()
        fmp2.onecmd("add dir/dir*/**")
        expected = ('.dir\\\\dir2\\x', '.dir\\\\dir2\\y', '.\\dir\\dir2\\z',
                    '.\\dir\\dir3\\1') 
        actual = zip(*fmp2.data.items())[0]
        self.assertEqual(actual, expected)
