# -*- coding: utf-8 -*-


import subprocess
import winreg
import re
import os
from functools import reduce


def makeStrFunction(builder, verbose=False):
    if verbose:
        return ''
    return (
        lambda targets, sources, env:
        '%s([%s], <sources are hidden>)' % (builder, ', '.join(["'" + str(t) + "'" for t in targets]))
        )


class SortedDict(dict):
    def __repr__(self):
        result = '{\n'
        sorted_keys = lambda x: sorted(zip(list(map(str, x)), x))
        for key_str, key in sorted_keys(list(self.keys())):
            result += '%s: %s,\n' % (key_str, self[key])
        result += '}'
        return result


JustPrintCmd = False
def pureLocalPopen(args, **kw):
    cwd = kw.get('cwd') or os.path.abspath(os.curdir)
    if type(args) != str:
        print('%s> %s' % (cwd, subprocess.list2cmdline(args)))
    else:
        print('%s> %s' % (cwd, args))
    if JustPrintCmd:
        return subprocess.Popen(['cmd.exe', '/Cexit'])
    return subprocess.Popen(
        args,
        **kw
    )

def pureLocalPopenPrintAndFail(args, **kw):
    cwd = kw.get('cwd') or os.path.abspath(os.curdir)
    if type(args) != str:
        print('%s> %s' % (cwd, subprocess.list2cmdline(args)))
    else:
        print('%s> %s' % (cwd, args))
    return None


################################################################
#TODO: include win32api with current local python version
def normalizePath(path):
    if path:
        return os.path.normpath(os.path.normcase(os.path.abspath(path)))
    else:
        return None


def getProcesses():
    import win32com.client

    WMI = win32com.client.GetObject('winmgmts:')
    processes = WMI.InstancesOf('Win32_Process')
    names = [process.Properties_('Name').Value for process in processes]
    paths = [process.Properties_('ExecutablePath').Value for process in processes]
    #cmdlines = [process.Properties_('CommandLine').Value for process in processes]
    paths = [normalizePath(x) for x in paths]

    res = dict(list(zip(paths, names)))

    return res


def ensureNotRunning(exe_path):
    import win32api
    import win32con

    exe_path = normalizePath(exe_path)

    processes = getProcesses()
    while exe_path in list(processes.keys()):
        name = processes[exe_path]
        message = '%s ("%s") is still running, please kill it to continue building' % (name, exe_path)
        print(message)
        result = win32api.MessageBox(
            0,
            message,
            'Build halted',
            win32con.MB_OKCANCEL + win32con.MB_ICONWARNING,
            0
        )
        if result == win32con.IDOK:
            processes = getProcesses()
            continue
        elif result == win32con.IDCANCEL:
            print('*** Cannot start compiling while exe still running')
            exit(1)
        else:
            assert False

################################################################


def runUnityEditorScript(methodPath, source_dir_path, env, **executeArgs):
    unity_path = env['UNITY_PATH']

    #TODO: include win32api with current local python version
    #ensureNotRunning(unity_path)

    #TODO: write log to separate file with date/time
    #'-logFile <pathname>',
    #   by http://docs.unity3d.com/Documentation/Manual/CommandLineArguments.html 
    #   otherwise read log from: http://docs.unity3d.com/Documentation/Manual/LogFiles.html
    args = [
        unity_path,
        '-quit',
        '-batchmode',
        '-projectPath', source_dir_path,
        '-executeMethod', methodPath,
    ]
    if len(executeArgs) > 0:
        args.append(
            '-customArgs:%s' % (';'.join(['%s=%s' % (str(k), str(executeArgs[k])) for k in list(executeArgs.keys())])))

    if env and env['debug']:
        args += [
            '--debug',
        ]
    p = pureLocalPopen(args=args)
    return p.wait()

#TODO: read log in thread to output it on the fly
def showUnityLog(rc):
    localappdata = os.getenv('LOCALAPPDATA')
    if not localappdata:
        print('**** LOCALAPPDATA environment variable is not found')
        return
    logpath = os.path.join(localappdata, 'Unity\Editor\Editor.log')
    if not os.path.exists(logpath):
        print('**** log is not found:', logpath)
        return
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    with open(logpath, 'rt') as f:
        print(f.read())
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(('' if rc == 0 else '****'), 'log path:', logpath)
    print()

def getMDTPath():
    try:
        probPath = r'C:\Program Files\Microsoft Deployment Toolkit'
        if (os.path.exists(probPath)):
            return probPath

        ## All this shit doesn't work, I dunno why currently, PortPy ruins registry HKLM processing some how ...
        '''
[19:18, 30.04.2020] Андрей Гришин: Пиздос ..... Ты не знаешь, в чем может быть прикол?
Запускаю я некий скрипт в powershell, который читает из реестра HKCU и HKLM 2 абсолютно идентичных значения, оба строки.
Если я скрипт исполняю из cmd line тупо - всё работает заебись.
Если я его исполняю из python27 просто установленного - всё заебись.
НО СУКА:
Если я его исполняю из PortPy нашего, то HKCU значения читаются, а HKLM - НЕТ.
Я попытался переключить функции RegOpenKey и иже с ними на варик из win32api - то же самое.
У меня просто ноль идей .... Что там такое PortPy руинит в своем енве или я хуй знает ...
[19:19, 30.04.2020] Андрей Гришин: И да, чтение что из питона что из powershell ведут себя одинаково, главное, кто изначально завел коляску. И наш portPy - единственный с проблемами
[19:20, 30.04.2020] Андрей Гришин: Но что еще веселее из HKLM он таки ВИДИТ сам ключ, и ОДНО значение из него (которое не строчка, а дворд), а все строчки НЕ видит (при энумерации всех значений в ключе)
        '''
        regKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Deployment 4')
        result = normalizePath(str(winreg.QueryValueEx(regKey, 'Install_Dir')[0]))
        if (not os.path.exists(result)):
            print(('ERROR: cannot find path [%s]' % result))
            return None

        return result
    except Exception as e:
        print(('ERROR: Failed to determine mdt path with exception: ' + repr(e)))
        return None

def getUnityPath():
    try:
        regKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Unity Technologies\Installer\Unity')

        version = str(winreg.QueryValueEx(regKey, 'Version')[0])
        rightVersion = '2019.4.21f1'  # '2019.2.17f1'
        if (version != rightVersion):
            print(('ERROR: You have wrong unity version installed, you version : [%s], required : [%s]' % (version, rightVersion)))
            return None

        unityDir = str(winreg.QueryValueEx(regKey, 'Location x64')[0])
        unityPath = os.path.join(unityDir, r'Editor\Unity.exe')
        if (not os.path.exists(unityPath)):
            print(('ERROR: cannot find file [%s]' % unityPath))
            return None

        return unityPath
    except Exception as e:
        print(('ERROR: Failed to determine unity path with exception: ' + repr(e)))
        return None

def extendEnvPath(pathlist):
    myEnv = os.environ.copy()
    for path in pathlist:
        myEnv['PATH'] += ';%s' % path
    print('!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(myEnv['PATH'])
    return myEnv


def _getQTBasePath():
    res = None
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'Applications\QtProject.QtCreator.c\Shell\Open\Command')
        res = str(winreg.QueryValueEx(key, None)[0])
    except:
        print('Cannot detect Qt base path!')
        return None
    qtCreatorExePath = res.split(' ')[0]
    baseQtSS = '\\\\'
    return qtCreatorExePath[:(qtCreatorExePath.find(baseQtSS))]


def getQTBaseBinFolder(qtVersion, qtProfile):
    basePath = _getQTBasePath()
    if not basePath:
        return None
    return os.path.join(basePath, qtVersion, qtProfile, 'bin')


def getQTQMakePath(qtVersion, qtProfile):
    res = os.path.join(getQTBaseBinFolder(qtVersion, qtProfile), 'qmake.exe')
    assert os.path.exists(res)
    return res


def getQTBuildPath(qtProfile):
    basePath = _getQTBasePath()
    if not basePath:
        return None
    res = None
    if qtProfile.startswith('msvc2017'):
        res = os.path.join(basePath, 'Tools', 'QtCreator', 'bin', 'jom.exe')
    elif qtProfile.startswith('msvc2012'):
        res = os.path.join(basePath, 'Tools', 'QtCreator', 'bin', 'jom.exe')
    else:
        res = os.path.join(basePath, 'Tools', 'mingw48_32', 'bin', 'mingw32-make.exe')
    assert os.path.exists(res)
    return res


########### helpers

def getByTemplate(regexTemplate, regexInnerPartsPatterns, content):
    result = []
    for iter in re.finditer(regexTemplate % regexInnerPartsPatterns, content):
        templatedContent = iter.group(0)
        for i in range(len(regexInnerPartsPatterns)):
            templatedContent = templatedContent.replace(iter.group(i + 1), '%s')
        result.append((
            iter.group(0),
            templatedContent,
            tuple([iter.group(i + 1) for i in range(len(regexInnerPartsPatterns))])
        ))
    return result


def directMult(iArr, jArr):
    return list(zip(reduce(lambda x, y: x + [y] * len(jArr), iArr, []), jArr * len(iArr)))


### shader compilation
def getFxcPath():
    InstallationFolder = None
    ProductVersion = None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Microsoft\Microsoft SDKs\Windows\v10.0')
        InstallationFolder = str(winreg.QueryValueEx(key, 'InstallationFolder')[0])
        ProductVersion = str(winreg.QueryValueEx(key, 'ProductVersion')[0])
    except:
        print('Cannot find win sdk version!')
    if ProductVersion:
        # The version can vary here with ".0" in the end
        path = os.path.join(InstallationFolder, 'bin', '%s.0' % ProductVersion, 'x64', 'fxc.exe')
        if os.path.exists(path):
            print('Found fxc path : %s' % path)
            return path
        else:
            print('ERROR: Found path does not exist : %s' % path)
    return None


def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


def flatten(l):
    return [j for sub in l for j in sub]


def fromPureCmdLine(s):
    return s.split(' ')
