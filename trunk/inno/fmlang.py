"""File-Mapper language.
This is a shell-like language used to generate a list of files of the form::
   destination: source

It can be used wherever you need to collect files and package them up for
distribution, and want a sane way to tell Python where files are coming from
and where they're going.
* Give commands one per line,
* Each command can have exactly one argument.  In some commands the
argument is optional, in others it is not.
* Commands that take glob arguments (all but chdir) can use the zsh-like
glob syntax ** to indicate recursion.  **/* matches all files in this
and subdirectories.
* Pound (#) may be used to denote comments, as in the Unix shell.
* Whitespace is ignored

The only commands it understands are:
  add [<glob>]
    grab all filenames (not names of directories) in this dir matching glob
  chdir (or cd) <dir>
    from now on, add all entries relative to this directory
  diradd [<glob>]
    add directories matching glob (not their contents--use for empty dirs)
  exclude <glob>
    from now on, don\'t grab any files that match this glob
  show
    print the current list of dest:source mappings to stdout
  unexclude <glob>
    stop excluding this glob, if it was previously excluded

Notes:

1. The file argument is optional for "(dir)add".  This is identical to
"(dir)add *".

2. "diradd" is distinct from add because it is only needed when you
have empty directories to add.  "add" keeps the directory structure
but only adds the files.

3. Shell ignoring of hidden files (named with a leading dot) does not
apply: * matches them.  Use "exclude .*" to exclude them.

4. The first quoted word after the command is taken as the glob pattern, and
everything after it is ignored.  Add quotes around patterns containing spaces.

5. The contents of the "current directory" (the argument to "chdir")
are added at the root level of the mapping.  To add make source file
in a subdirectory of the destination, use "add subdir/file", NOT
"chdir subdir" followed by "add file".

6. If replaceDuplicates==1, silently replace duplicate destination files with
new source files.  If replaceDuplicates==0 (default), raise an exception when
two different source files are added for the same destination file.

Example::
  chdir /etc
  exclude *i*
  add *tab # everything but inittab
  diradd cron.d
  add pam.d/p*
  chdir X11
  unexclude *i*
  add X*
The above might produce::
[('fstab',            '/etc/fstab'),
 ('mtab',             '/etc/mtab'),
 ('crontab',          '/etc/crontab'),
 ('cron.d/',          '/etc/cron.d/'),
 ('pam.d/passwd',     '/etc/pam.d/passwd'),
 ('pam.d/ppp',        '/etc/pam.d/ppp'),
 ('XF86Config',       '/etc/X11/XF86Config'),
 ('XftConfig',        '/etc/X11/XftConfig'),
 ('Xsession.options', '/etc/X11/Xsession.options'),
 ('Xwrapper.config',  '/etc/X11/Xwrapper.config')]
"""
from itertools import chain

import os
import cmd
import shlex
from cStringIO import StringIO
import re
import fnmatch

from inno.path import path

def gatherHits(curdir, components, xglobs=()):
    if len(components)==0:
        return []
    gathered = OrderedDict()
    add = lambda d,s: gathered.__setitem__(str(d), str(s))
    here = path(curdir)
    comp = path(components.pop(0))
    # the rule is:
    # 1. normal globs match files or dirs in the current directory
    # 2. ** recursive globs match any dir in the subtree including '.'
    # 3. unless there are no components left to process, in which case
    #    treat as a normal glob.
    if len(components)==0:
        matcher = here.listdir
    else:
        if str(comp)=='**':
            matcher = lambda g: chain((here,), here.walkdirs(g))
        else:
            matcher = here.dirs
    xrelist = [] # list of regular expressions for matching excluded files
    for xg in xglobs:
        cre = re.compile(fnmatch.translate(xg))
        xrelist.append(cre)
    for f in matcher(comp):
        excluded = 0
        # filter with xglobs
        for xg, xg_re in zip(xglobs, xrelist):
            if re.match(xg_re, f) or f.fnmatch(xg):
                excluded = 1
                break
        if not excluded:
            add(f, f.abspath())
            if f.isdir():
                for d, s in gatherHits(f, components[:], xglobs):
                    add(d,s)
    return gathered.items()
    
    

def matches(curdir, glob, xglobs=()):
    """Return the entries that match glob and do not match any xglob"""
    old = os.getcwd()
    os.chdir(curdir)
    try:
        # sanity check.. make sure glob uses os.sep
        if glob in ('', None): glob = '*'
        glob = path(glob).normpath()
        components = str(glob).split(os.sep)
        return gatherHits('.', components, xglobs)
    finally:
        os.chdir(old)

wordchars = ''.join([chr(n) for n in range(255)
                     if n not in (9,10,13,32,34,39)])

def cleanLine(line):
    """pass line through shlex to get rid of comments and extra args"""
    sio = StringIO(line)
    lexer = shlex.shlex(sio)
    lexer.wordchars = wordchars
    # lexer.debug = 1
    gt = lexer.get_token
    # in non-posix shlex returns None for EOF, so kludge with {or ''}
    cmd, arg = gt() or '', gt() or ''
    if len(arg)>=1 and arg[0] in lexer.quotes:
        arg = arg[1:-1]
    return ' '.join((cmd, arg))


class FileMapperParser(cmd.Cmd):
    """An implementation of the FileMapper command set.  Use
    FileMapperParser.onecmd(s) to issue a command.
    """
    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.exclusions = []
        self.replaceDuplicates = 0
        self.data = OrderedDict()
        self.cwd = path('.')

    def parseline(self, line):
        line = cleanLine(line)
        pos = line.find(' ')
        word1 = line[:pos]
        word2 = line[pos+1:]
        return word1 or None, word2 or None, line.strip()

    def _update(self, dct):
        if not self.replaceDuplicates:
            dupes = [(k,dct[k],self.data[k]) for k in dct if k in self.data]
            if dupes:
                raise DuplicateFileException(dupes)
        self.data.update(dct)

    def do_add(self, glob):
        """grab all files (not subdirectories) in this dir matching the
        glob
        """
        hits = matches(self.cwd, glob, self.exclusions)
        [hits.remove(x) for x in hits[:] if path(x[1]).isdir()]
        self._update(OrderedDict(hits))

    def do_chdir(self, directory):
        """from now on, add all entries relative to this directory"""
        new_cwd = (self.cwd / directory).normpath()
        if not new_cwd.isdir():
            raise InvalidDirectoryException(new_cwd)
        self.cwd = new_cwd
    do_cd = do_chdir
    
    def do_diradd(self, glob):
        """add directories matching this glob (not its contents -
        use for empty dirs)
        """
        hits = []
        for m in matches(self.cwd, glob, self.exclusions):
            hits.append((m[0] + os.sep, m[1]))
        [hits.remove(x) for x in hits[:] if path(x[1]).isfile()]
        self._update(OrderedDict(hits))
        
    def do_exclude(self, glob):
        """from now on, don't grab any files that match this glob"""
        # TODO - this should probably raise an error if glob is missing
        self.exclusions.append(glob)

    def do_unexclude(self, glob):
        """stop excluding this glob, if it was previously excluded"""
        # TODO - this should probably raise an error if glob is missing
        if glob in self.exclusions:
            self.exclusions.remove(glob)

    def do_show(self, glob):
        """Return the list"""
        r = []
        for d,s in self.data.items():
            print "%24s: %s" % (d, s)

    def emptyline(self):
        """Don't repeat the last command"""
        pass

class DuplicateFileException(Exception):
    def __init__(self, items):
        self.items = items
    def __str__(self):
        return "Attempt to add different files at the same destination"

class InvalidDirectoryException(Exception):
    def __init__(self, dirname):
        self.dirname = dirname
    def __str__(self):
        return "Tried to change into directory %s which does not exist" % self.dirname


class OrderedDict(dict):
    """A dict which you can access in order through items() or popitem().
    Supports all normal dict operations, but keep in mind that if you update()
    it from a regular (non-ordered) dict, the new items will not be in any
    order (but will follow all the old items). Updating from another
    OrderedDict will preserve the order of both dicts.
    """
    def __init__(self, t=()):
        self.order = []
        for k, v in t:
            self[k] = v
        
    def __setitem__(self, k, v): 
        # Replacing items with the same value changes the order, so don't
        # replace items 
        if k in self.keys() and v==self[k]:
            return
        dict.__setitem__(self, k, v)
        if k in self.order:
            self.order.remove(k)
        self.order.append(k)
    def __delitem__(self, k):
        dict.__delitem__(self, k)
        self.order.remove(k)
    def items(self):
        """Return a list with the dict's items, in order"""
        return [(k, dict.get(self, k)) for k in self.order]
    def copy(self):
        new1 = WhinyOrderedDict()
        for k, v in self.items():
            new1[k] = v
        return new1
    def update(self, d):
        for k,v in d.items(): self[k] = v
    def clear(self):
        r = dict.clear(self)
        self.order = []
        return r
    def popitem(self):
        k, v = self.items()[0]
        del self[k]
        return k, v

# utilities for processing fmscript with the parser
def sourceItems(fmscript, replaceDuplicates=0):
    """Return only the source files matched by the fmscript"""
    fmp = FileMapperParser()
    fmp.replaceDuplicates = replaceDuplicates
    [fmp.onecmd(l) for l in fmscript.splitlines()]
    return zip(*fmp.data.items())[0]

