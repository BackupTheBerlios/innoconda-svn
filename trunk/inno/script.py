"""Create (very basic) Inno Setup scripts from parameters"""
from __future__ import generators

# stdlib imports
import os
from cStringIO import StringIO
import tempfile
import types

# local imports
from inno.path import path
import inno

def dumbPrefixedMethods(instance, prefix):
    klass = instance.__class__
    for name, obj in klass.__dict__.items():
        if type(obj) is types.FunctionType and name.startswith(prefix):
            yield getattr(instance, name)

class Script:
    """A scriptable inno setup script (.iss).
    >>> from inno import Script
    >>> s = Script(display_name=\"My Program\", name=\"myprogram\",
    package_version=\"1.0\", destination=\"{pf}\myprogram\")
    >>> s.collect(\"myprogram\") # add files to the package
    >>> s.compile() # run inno on the package
    """
    _required = ('display_name', 'name', 'package_version',
                 'destination',)
    def __init__(self, **options):
        for a in self._required: setattr(self, a, options[a])
        self.uninstallable = options.get('uninstallable', 1)
        self._options = options
        self.sources = []

    def collect(self, src, recurse=1, empties=1, exclude_globs=()):
        """Use files in src as the content of the Inno script.
The script will use every file in that directory, and (by default) its
subdirectories.  You can call this more than once to collect
several directories.
@param src: stuff to package
@param recurse: Whether to descend subdirectories
@param empties: Whether to keep empty directories in the package
@param exclude_globs: list of patterns relative to src which will be
packaged (dirs or files)
@type exclude_globs: iterable
"""
        self._base = psrc = path(src)

        assert psrc.isdir()

        def filtername(pth):
            for pat in exclude_globs:
                if pth.fnmatch(pat):
                    return 0
            return 1

        all_dirs = list(psrc.walkdirs())
        filtered_dirs = [d for d in all_dirs if filtername(d)]
        
        for d in [psrc] + filtered_dirs:
            all = d.files()
            filtered = [f for f in all if filtername(f)]
            self.sources.extend(filtered)
            if empties and len(filtered) == 0:
                self.sources.append(d)
        
    def writeScript(self, fd):
        """Serialize script to fd
        @param fd: filelike object with write() method
        """
        w = fd.write
        self._options['absbase'] = self._base.abspath()
        self._options['workdir'] = os.getcwd()
        w("""\
[Setup]
AppName=%(display_name)s
AppVerName=%(display_name)s %(package_version)s
DefaultDirName=%(destination)s
SourceDir=%(absbase)s
OutputBaseFilename=%(name)s-%(package_version)s-setup
DefaultGroupName=%(display_name)s
OutputDir=%(workdir)s
""" % self._options)
        if not self.uninstallable:
            w("Uninstallable=false")
        for m in dumbPrefixedMethods(self, "_section_"):
            m(fd)

    def _section_Files(self, fd):
        w = fd.write
        w("[Files]\n")

        tmpl = 'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion\n'
        for f in self.sources:
            if f.isfile():
                source = self._base.relpathto(f)
                w(tmpl % (source, os.path.dirname(source)))
    
    def _section_Dirs(self, fd):
        w = fd.write
        w("[Dirs]\n")

        tmpl = 'Name: "{app}\%s"\n'
        for d in self.sources:
            if d.isdir():
                ## FIXME? 2 leading slashes is bad, might have to clean up
                source = self._base.relpathto(d)
                w(tmpl % source)

    def _section_Icons(self, fd):
        w = fd.write
        w("[Icons]\n")
        if self.uninstallable:
            w('Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"\n' %
              self.display_name)

    def compile(self, noTemporary=1):
        """Generate the script file and send it to iscc
        @param noTemporary: give the .iss file a real name and don't delete
        it
        """
        if noTemporary:
            out = file("%s.iss" % self.name, 'w+')
        else:
            out = tempfile.NamedTemporaryFile(suffix='.iss', mode='w+')
        name = out.name
        self.writeScript(out)
        out.close()
        inno.build(name)
