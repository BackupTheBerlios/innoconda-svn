"""File-Mapper language.
This is a shell-like language used to generate a list of files of the form::
   source: destination

It can be used wherever you need to collect files and package them up for
distribution, and want a sane way to tell Python where files are coming from
and where they're going.
* Give commands one per line,
* consisting of a single word followed by a single file pattern possibly
containing wildcards, otherwise known as a glob.  (chdir is the only
command that does not take a glob, it must take a directory)
* Pound (#) may be used to denote comments, as in the Unix shell.
* Whitespace is ignored

The only commands it understands are:
  add
    grab all files (not subdirectories) in this dir matching the glob
  chdir (or cd)
    from now on, add all entries relative to this directory
  diradd
    add directories matching this glob (not its contents - use for empty dirs)
  dirrecurse
    add all directories matching this glob, in this dir and subdirectories
  exclude
    from now on, don't grab any files that match this glob
  recurse
    add all files matching this glob, in this dir and subdirectories
  unexclude
    stop excluding this glob, if it was previously excluded

Notes:

1. The file argument is optional for "(dir)add", "(dir)recurse".  This is
identical to "(dir)add *" and "(dir)recurse *", respectively.

2. "diradd" and "dirrecurse" are distinct from add and recurse because they
are only needed when you have empty directories to add.  "add" and "recurse"
keep the directory structure but only add the files.

3. Shell matching of hidden files (named with a leading dot) do not
apply: * matches them.  Use "exclude .*" to exclude them.

4. The first quoted word after the command is taken as the glob pattern, and
everything after it is ignored.  Add quotes around patterns containing spaces.

5. The contents of the "current directory" (the argument to "chdir") are added
at the root level of the mapping.  To add a directory in a subdirectory, use
"add subdir/file", NOT "chdir subdir" followed by "add file".

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
import os
import cmd
import shlex
from cStringIO import StringIO

from inno.path import path


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
        # Replacing items changes the order, so don't replace items
        if k in self and v==self[k]:
            return
        dict.__setitem__(self, k, v)
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


def matches(funk, curdir, glob, xglobs=()):
    """Return the entries that match glob and do not match any xglob"""
    old = os.getcwd()
    os.chdir(curdir)
    try:
        dn, bn = path(glob).splitpath()
        dn = dn or path('.') # '' is not a valid dir, so replace with '.'
        all = getattr(dn, funk)(bn)
        allcopy = list(all)
        for xg in xglobs:
            for f in allcopy[:]:
                if f.fnmatch(xg):
                    allcopy.remove(f)
        return [(str(f)+ os.sep * f.isdir(), # add a slash to dirs
                str(f.abspath())) for f in allcopy
                ]
    finally:
        os.chdir(old)

matchesf = lambda cwd, g, xg=(): matches("files", cwd, g, xg)
matchesd = lambda cwd, g, xg=(): matches("dirs", cwd, g, xg)
deepmatchesf = lambda cwd, g, xg=(): matches("walkfiles", cwd, g, xg)
deepmatchesd = lambda cwd, g, xg=(): matches("walkdirs", cwd, g, xg)

wordchars = ''.join([chr(n) for n in range(255)
                     if n not in (9,10,13,32,34,39)])

def cleanLine(line):
    """pass line through shlex to get rid of comments and extra args"""
    sio = StringIO(line)
    lexer = shlex.shlex(sio)
    lexer.wordchars = wordchars
    #lexer.debug = 1
    gt = lexer.get_token
    # in non-posix shlex returns None for EOF, so kludge with {or ''}
    # try posix?
    cmd, arg = gt() or '', gt() or ''
    if len(arg)>=1 and arg[0] in lexer.quotes:
        arg = arg[1:-1]
    return ' '.join((cmd, arg))

def xparseLine(line):
    pos = line.find(' ')
    word1 = line[:pos]
    word2 = line[pos+1:]
    return word1 or None, word2 or None, line.strip()

class FileMapperParser(cmd.Cmd):
    
    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.exclusions = []
        self.replaceDuplicates = 0
        self.data = OrderedDict()
        self.cwd = path('.')

    def parseline(self, line):
        return xparseLine(cleanLine(line))

    def _update(self, dct):
        if '__init__.py' in dct: import pdb; pdb.set_trace() ##################
        if not self.replaceDuplicates:
            dupes = [(k,dct[k],self.data[k]) for k in dct if k in self.data]
            if dupes:
                raise DuplicateFileException(dupes)
        self.data.update(dct)

    def do_add(self, glob):
        """grab all files (not subdirectories) in this dir matching the
        glob
        """
        if glob in ('', None): glob = '*'
        od = OrderedDict(matchesf(self.cwd, glob, self.exclusions))
        self._update(od)

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
        if glob in ('', None): glob = '*'
        od = OrderedDict(matchesd(self.cwd, glob, self.exclusions))
        self._update(od)
        
    def do_dirrecurse(self, glob):
        """add all directories matching this glob, in this dir
        and subdirectories
        """
        if glob in ('', None): glob = '*'
        od = OrderedDict(deepmatchesd(self.cwd, glob, self.exclusions))
        self._update(od)
        
    def do_exclude(self, glob):
        """from now on, don't grab any files that match this glob"""
        self.exclusions.append(glob)
        
    def do_recurse(self, glob):
        """add all files matching this glob, in this dir and subdirectories
        unexclude
        """
        if glob in ('', None): glob = '*'
        od = OrderedDict(deepmatchesf(self.cwd, glob, self.exclusions))
        self._update(od)
        
    def do_unexclude(self, glob):
        """stop excluding this glob, if it was previously excluded"""
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
