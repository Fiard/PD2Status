from Python import common
from Python.utils import *

print('Starting sym links ...')

symConfig = [{
    'from' : os.path.join(common.ROOT_PROJ, r'..\NovaPD2Tunnel'),
    'to' : os.path.join(common.ROOT_PROJ, r'PD2Status'),
    'name' : 'Nova',
}]

for config in symConfig:
    fr = config['from']
    to = config['to']
    name = config['name']
    resLinkFolder = os.path.join(to, name)
    if not os.path.exists(resLinkFolder):
        print ('Creating SymLink for [%s] [(%s) -> (%s)]' % (name, fr, resLinkFolder))
        if not os.path.exists(to):
            os.makedirs(to)
        subprocess.check_call('mklink /J "%s" "%s"' % (name, fr), cwd = to, shell = True)

print ('Sym links complete!')
