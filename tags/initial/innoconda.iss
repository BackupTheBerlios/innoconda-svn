[Setup]
AppName=Innoconda
AppVerName=Innoconda 0.1.0
DefaultDirName={code:PythonDir}\inno
SourceDir=C:\cygwin\home\PASS Program\cvs\Innoconda\inno
OutputBaseFilename=innoconda-0.1.0-setup
DefaultGroupName=Innoconda
OutputDir=C:\cygwin\home\PASS Program\cvs\Innoconda
[Icons]
Name: "{group}\Uninstall Innoconda"; Filename: "{uninstallexe}"
[Dirs]
Name: "{app}\test"
Name: "{app}\program\Examples\MyDll"
[Files]
Source: "path.py"; DestDir: "{app}\"; Flags: ignoreversion
Source: "__init__.py"; DestDir: "{app}\"; Flags: ignoreversion
Source: "process.py"; DestDir: "{app}\"; Flags: ignoreversion
Source: "THIRDPARTY.txt"; DestDir: "{app}\"; Flags: ignoreversion
Source: "LICENSE.inno"; DestDir: "{app}\"; Flags: ignoreversion
Source: "LICENSE.process"; DestDir: "{app}\"; Flags: ignoreversion
Source: "LICENSE.innoconda"; DestDir: "{app}\"; Flags: ignoreversion
Source: "version.py"; DestDir: "{app}\"; Flags: ignoreversion
Source: "runner.py~"; DestDir: "{app}\"; Flags: ignoreversion
Source: "__init__.pyc"; DestDir: "{app}\"; Flags: ignoreversion
Source: "process.pyc"; DestDir: "{app}\"; Flags: ignoreversion
Source: "path.pyc"; DestDir: "{app}\"; Flags: ignoreversion
Source: "script.py~"; DestDir: "{app}\"; Flags: ignoreversion
Source: "version.pyc"; DestDir: "{app}\"; Flags: ignoreversion
Source: "runner.py"; DestDir: "{app}\"; Flags: ignoreversion
Source: "runner.pyc"; DestDir: "{app}\"; Flags: ignoreversion
Source: "script.py"; DestDir: "{app}\"; Flags: ignoreversion
Source: "script.pyc"; DestDir: "{app}\"; Flags: ignoreversion
Source: "test\data\simple.iss"; DestDir: "{app}\test\data"; Flags: ignoreversion
Source: "program\Compil32.exe"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\Default.isl"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\isbunzip.dll"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\isbzip.dll"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\ISCC.exe"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\ISCmplr.dll"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\ISetup.cnt"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\isetup.GID"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\ISetup.hlp"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\isfaq.htm"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\RegSvr.e32"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\Setup.e32"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\SetupLdr.e32"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\Uninst.e32"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\whatsnew.htm"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\WizModernImage.bmp"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\WizModernImage2.bmp"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\WizModernSmallImage.bmp"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\WizModernSmallImage2.bmp"; DestDir: "{app}\program"; Flags: ignoreversion
Source: "program\Examples\Example2.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\Example3.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\ISPPExample1.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\ISPPExample1License.txt"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\MyDll.dll"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\MyProg.exe"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\MyProg.hlp"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\Readme.txt"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\CodeClasses.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\CodeDlg.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\CodeDll.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\CodeExample1.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\Example1.iss"; DestDir: "{app}\program\Examples"; Flags: ignoreversion
Source: "program\Examples\MyDll\C\MyDll.c"; DestDir: "{app}\program\Examples\MyDll\C"; Flags: ignoreversion
Source: "program\Examples\MyDll\C\MyDll.def"; DestDir: "{app}\program\Examples\MyDll\C"; Flags: ignoreversion
Source: "program\Examples\MyDll\C\MyDll.dsp"; DestDir: "{app}\program\Examples\MyDll\C"; Flags: ignoreversion
Source: "program\Examples\MyDll\C\MyDll.dsw"; DestDir: "{app}\program\Examples\MyDll\C"; Flags: ignoreversion
Source: "program\Examples\MyDll\Delphi\MyDll.dpr"; DestDir: "{app}\program\Examples\MyDll\Delphi"; Flags: ignoreversion
