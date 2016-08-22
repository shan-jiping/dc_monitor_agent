# -*- coding: utf-8 -*-
import json,urllib,httplib,yaml


class saltNet(object):
    '''
    使用http调用saltapi
    '''


    def __init__(self, host,port,username,passwd):
        '''
        设置参数
        '''
        self.host=host
        self.port=port
        self.username=username
        self._password=passwd
        
     
    def _getauth(self):
        '''
        申请token
        '''
        params = urllib.urlencode({"username":self.username,"password":self._password,"eauth":"pam"})

        headers = {'Accept':'application/x-yaml','Content-Type': 'application/x-www-form-urlencoded'}
        #headers={"Content-type": "application/x-www-form-urlencoded","Accept":"text/plain"}
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("POST", "/login",params,headers)
        try:
            r1 = conn.getresponse()
            data1 = r1.read()
            conn.close()     
            return yaml.load(data1)['return'][0]['token']
        except Exception,e:
            conn.close()
            return e
        
    def run(self,params_dict):
        token=self._getauth()
        params=json.dumps(params_dict)
        #params = urllib.urlencode(params_dict)
        headers = {'Accept':'application/x-yaml','Content-Type': 'application/json','X-Auth-Token':token}
        conn = httplib.HTTPConnection(self.host,self.port)
        conn.request("POST", "/",params,headers)
        try:
            r1 = conn.getresponse()
            data1 = r1.read()
            conn.close()     
            return data1
        except Exception,e:
            conn.close()
            return e
        
class saltHost(saltNet):
    def __init__(self, host,port,username,passwd):
        saltNet.__init__(self,host,port,username,passwd)
    
    def run(self,params_dict):
        return yaml.load(saltNet.run(self,params_dict))['return'][0]
    
    def syncHost(self):
        params_dict={'fun':'host.sync','client':'local','tgt':'*'}
        return saltNet.run(self, params_dict)
    
    def pingHost(self,hostname):
        params_dict={'fun':'test.ping','client':'local','tgt':hostname}
        return saltNet.run(self, params_dict)
    
    
    def saltssh(self,cmd,hostname,arg=None):
        params_dict={'fun':cmd,'client':'ssh','tgt':hostname,'arg':arg}
        return saltNet.run(self, params_dict)
    
    def saltSshstatebase(self,hostname,sls):
        params_dict={'fun':'state.sls','client':'ssh','tgt':hostname,'arg':sls}
        return saltNet.run(self, params_dict)
    
    def saltstateprod(self,hostname,sls):
        params_dict={'fun':'state.sls','client':'local','tgt':hostname,'arg':sls,'kwarg':{'saltenv':'prod'}}
        return saltNet.run(self, params_dict)
    
    def saltstatetest(self,hostname,sls):
        params_dict={'fun':'state.sls','client':'local','tgt':hostname,'arg':sls,'kwarg':{'saltenv':'test'}}
        return saltNet.run(self, params_dict)
    
    def saltcmdrun(self,hostname,cmd):
        params_dict={'fun':'key.list_all','client':'wheel','tgt':hostname}
        return saltNet.run(self, params_dict)
    
#list=['initial']
#listHostDetail=['docker:Version','saltversion']
#dictHostDetail={'fun':'grains.item','client':'local','tgt':'jsjyw-jycloud-190','arg':listHostDetail}
#print saltHost('10.10.20.190',8000,'api','api123qwe').run(dictHostDetail)
#a=saltHost('192.168.9.149',8000,'api','api123qwe').accept_salt_clientkey('yumRepoServer50'
#for x in yaml.load(a)['return'][0]['saltmaster-9-149']['mem']:
#    print x


