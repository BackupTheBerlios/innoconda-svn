"""Create (very basic) Inno Setup scripts from parameters"""
# stdlib imports
import os
from cStringIO import StringIO
import tempfile
import types

# local imports
from inno.path import path
from inno.fmlang import FileMapperParser
import inno


def prefixedMethods(obj, prefix):
    """A list of methods with a given prefix on a given instance.
    """
    dct = {}
    accumulateMethods(obj, dct, prefix)
    return dct.values()

def accumulateMethods(obj, dict, prefix='', curClass=None):
    """accumulateMethods(instance, dict, prefix)
    I recurse through the bases of instance.__class__, and add methods
    beginning with 'prefix' to 'dict', in the form of
    {'methodname':*instance*method_object}.
    """
    if not curClass:
        curClass = obj.__class__
    for base in curClass.__bases__:
        accumulateMethods(obj, dict, prefix, base)

    for name, method in curClass.__dict__.items():
        optName = name[len(prefix):]
        if ((type(method) is types.FunctionType)
            and (name[:len(prefix)] == prefix)
            and (len(optName))):
            dict[optName] = getattr(obj, name)

class Script:
    """A scriptable inno setup script (.iss).
    >>> from inno import Script
    >>> s = Script(display_name=\"My Program\", name=\"myprogram\",
    package_version=\"1.0\")
    >>> s.collect(\"myprogram\") # add files to the package
    >>> s.compile() # run inno on the package
    """
    _required = ('display_name', 'name', 'package_version',)
    def __init__(self, **options):
        for a in self._required: setattr(self, a, options[a])
        self.uninstallable = options.get('uninstallable', 1)
        if not options.get('destination', None):
            options['destination'] = r"{pf}\%(name)s" % options
        self._options = options
        self.sources = []
        self.fmscript = None

    def runFileCommands(self):
        """Process self.fmscript as a FileMapper script (fmlang.py),
        storing the result in self.sources
        """
        fmp = FileMapperParser()
        for line in self.fmscript.split('\n'):
            fmp.onecmd(line)
        
        self.sources = fmp.data.items()
        

    def collect(self, src, recurse=1, empties=1, exclude_globs=()):
        """Add files in src as contents of the Inno package.
The script will use every file in that directory, and (by default) its
subdirectories.  You can call this more than once to collect
several directories.
@param src: stuff to package
@param recurse: Whether to descend subdirectories
@param empties: Whether to keep empty directories in the package
@param exclude_globs: list of patterns relative to src which will *not* be
packaged
@type exclude_globs: iterable
"""
        scx = []
        do = scx.append
        
        do("chdir '%s'" % src)
        for xg in exclude_globs:
            do("exclude '%s'" % xg)

        if recurse and not empties:
            do("recurse")
        elif recurse and empties:
            do("recurse"); do("dirrecurse")
        elif not recurse and not empties:
            do("add")
        elif not recurse and empties:
            do("add"); do("diradd")

        self.fmscript = '\n'.join(scx)

        self.runFileCommands()
        
    def writeScript(self, fd):
        """Serialize script to fd
        @param fd: filelike object with write() method
        """
        for m in prefixedMethods(self, "_section_"):
            m(fd)

    def _section_Setup(self, fd):
        w = fd.write
        self._options['workdir'] = os.getcwd()
        w("""\
[Setup]
AppName=%(display_name)s
AppVerName=%(display_name)s %(package_version)s
DefaultDirName=%(destination)s
OutputBaseFilename=%(name)s-%(package_version)s-setup
DefaultGroupName=%(display_name)s
OutputDir=%(workdir)s
""" % self._options)
        if not self.uninstallable:
            w("Uninstallable=false")
        

    def _section_Files(self, fd):
        w = fd.write
        w("[Files]\n")

        tmpl = 'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion\n'
        for dest, src in self.sources:
            if path(src).isfile():
                w(tmpl % (src, path(dest).dirname()))

    def _section_Dirs(self, fd):
        w = fd.write
        w("[Dirs]\n")

        tmpl = 'Name: "{app}\%s"\n'
        for dest, src in self.sources:
            if path(dest).isdir():
                w(tmpl % dest)

    def _section_Icons(self, fd):
        w = fd.write
        w("[Icons]\n")
        if self.uninstallable:
            w('Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"\n' %
              self.display_name)

    def compile(self, temporary=0):
        """Generate the script file and send it to iscc
        @param temporary: use a temp file for the iss
        """
        if temporary:
            out = tempfile.NamedTemporaryFile(suffix='.iss', mode='w+')
        else:
            out = file("%s.iss" % self.name, 'w+')
        name = out.name
        self.writeScript(out)
        out.close()
        inno.build(name)

class PythonScript(Script):
    def _section_Types(self, fd):
        fd.write('''\
[Types]
Name: "2.2"; Description: "Install for Python 2.2"; Check: Python22Available
Name: "2.3"; Description: "Install for Python 2.3"; Check: Python23Available
''')
    def _section_Components(self, fd):
        fd.write('''\
[Components]
Name: "python2.2"; Description: "Python 2.2"; Types: 2.2; Flags: exclusive
Name: "python2.3"; Description: "Python 2.3"; Types: 2.3; Flags: exclusive
''')
    def _section_Messages(self, fd):
        fd.write('''\
[Messages]
WizardSelectComponents=Select Python Version
SelectComponentsDesc=For which Python version will you install this package?
SelectComponentsLabel2=Select a version of Python.
NoUninstallWarningTitle=Previously Installed
NoUninstallWarning=Setup has detected that this package has already been installed for:%n%1%n%nIf you later uninstall this package, both versions wil be uninstalled at once.%nSelect "Yes" to continue (this is safe).
''')

    def _section_Files(self, fd):
        w = fd.write
        w("[Files]\n")

        tmpl = 'Source: "%s"; DestDir: "{code:SiteLib}\%s"; Flags: ignoreversion\n'
        for dest, src in self.sources:
            if path(src).isfile():
                w(tmpl % (src, path(dest).dirname()))

    def _section_Setup(self, fd):
        Script._section_Setup(self, fd)
        fd.write("DisableDirPage=yes\n")

    def _section_Code(self, fd):
        fd.write(r"""[Code]
var
  selectedPythonDir: String;

function findPython(version: String): String;
begin
   {try HKLM first and then fall back to HKCU for location of Python}
   Result := ExpandConstant('{reg:HKLM\Software\Python\PythonCore\' + version + '\InstallPath,|ACK}')
   if CompareStr(Result, 'ACK')=0 then
      Result := ExpandConstant('{reg:HKCU\Software\Python\PythonCore\' + version + '\InstallPath,|ACK}');
end;

function SiteLib(Default: String): String;
begin
  selectedPythonDir := findPython(WizardSetupType(False));
  Result := selectedPythonDir + '\lib\site-packages\inno';
end;

function Python22Available(): Boolean;
begin
  Result := True;
  if CompareStr(findPython('2.2'), 'ACK')=0 then
    Result := False;
end;

function Python23Available(): Boolean;
begin
  Result := True;
  if CompareStr(findPython('2.3'), 'ACK')=0 then
    Result := False;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not Python22Available and not Python23Available then
  begin;
    MsgBox('No versions of Python were found.  Cannot continue.', mbCriticalError, MB_OK);
    Result:=False;
  end;
end;

""")
