import os

from inno.process import ProcessOpen
from inno.path import path

def sibpath(file1, name):
    return path(file1).dirname()/path(name)

iscc = str(sibpath(__file__, "program")/"ISCC.exe")

def build(script):
    po = ProcessOpen((iscc, script))
    print po.stdout.read()
    status = po.wait()
    assert status==0
