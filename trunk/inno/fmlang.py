"""File-Mapper language.
This is a shell-like language used to generate a list of files of the form::
   source: destination

It can be used wherever you need to collect files and package them up for
distribution, and want a sane way to tell Python where files are coming from
and where they're going.
* Give commands one per line,
* consisting of a single word followed by a single file pattern possibly
containing wildcards, otherwise known as a glob.
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

import cmd
import shlex
from cStringIO import StringIO

from inno.path import path

def cleanLine(line):
    """pass line through shlex to get rid of comments and extra args"""
    sio = StringIO(line)
    gt = shlex.shlex(sio).get_token
    cmd, arg = gt(), gt()
    if arg[0] in ('"', "'"):
        arg = arg[1:-1]
    # python 2.2's shlex returns None for EOF, so kludge with {or ''}
    return ' '.join((cmd or '', arg or ''))

class FileMapperParser(cmd.Cmd):
    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.data = []
        self.exclusions = []
        
    def parseline(self, line):
        return cmd.Cmd.parseline(self, cleanLine(line))

    def do_add(self, glob):
        """grab all files (not subdirectories) in this dir matching the
        glob
        """
    def do_chdir(self, glob):
        """from now on, add all entries relative to this directory"""
    do_cd = do_chdir
    
    def do_diradd(self, glob):
        """add directories matching this glob (not its contents -
        use for empty dirs)
        """
    def do_dirrecurse(self, glob):
        """add all directories matching this glob, in this dir
        and subdirectories
        """
    def do_exclude(self, glob):
        """from now on, don't grab any files that match this glob"""
        self.exclusions.append(glob)
    def do_recurse(self, glob):
        """add all files matching this glob, in this dir and subdirectories
        unexclude
        """
    def do_unexclude(self, glob):
        """stop excluding this glob, if it was previously excluded"""
        if glob in self.exclusions:
            self.exclusions.remove(glob)
        
    def emptyline(self):
        """Don't repeat the last command"""
        pass

class DuplicateFileException(Exception):
    pass
