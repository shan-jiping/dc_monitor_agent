# -*- coding: utf-8 -*-
#import  pxssh
from salt.scripts import salt_ssh
import yaml



        
class roster(object):
    """����rosterΪ����salt-ssh��׼��,rosterfiler�����Զ������nfs
    """
    def __init__(self,rosterfile):
        self.rosterfile=rosterfile
        
    def write(self,clientName,clientIP,clientUser='root',clientPasswd='666666',clientSudo=False):
        data={clientName: {'host':clientIP,'user':clientUser,'passwd':clientPasswd,'sudo':clientSudo }}
        try:
            with open(self.rosterfile,'w') as f:
                yaml.dump(data,f,default_flow_style=False)
            return 'ok'
        except Exception,e:
            return 'Roster file write: '+ e
            
    def load(self):
        try:
            with open(self.rosterfile,'r') as f:
                data=yaml.load(f)
            return data
        except Exception,e:
            return 'Roster file read: '+ e    
        
    
        

#print saltNet.saltHost('192.168.9.149',8000,'api','api123qwe').saltssh('items.grains', 'yum')

#print roster('Y:\\roster').write('yum', '192.168.9.50','root','JYall^9_system!@#yh$')