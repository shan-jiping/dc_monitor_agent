# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
'''
Created on 2016年3月16日

@author: wang.shiyi
'''
import docker

from time import sleep

import logging
from model import *



##global declare_namespace
#ipAdd='unix://var/run/docker.socket'
#DBconf='mysql://w11:w11@10.10.20.67:3306/dockerM'
#version='1.20'

class dockerBase(object):
    '''
    base class
    '''
    def __init__(self,ipAdd,version):
        '''
        estiblish client for the docker api
        '''
        self.ipAdd=ipAdd
        self.version=version
        self.cli = docker.Client(base_url=ipAdd,version=version)
    

    def versionD(self):
        print 'w11'
        cli=self.cli
        
        return cli.version()

    def contain(self):
        '''
        get the container of the docker
        '''
        docker_list={}
        cli=self.cli
        for x in cli.containers():
            docker_list[x['Id'][:12]]=x
        return docker_list

    def dc_info(self):
        '''
        docker info
        '''
        cli=self.cli
        return cli.info()

    def stat(self,docker_id):
        '''
        docker stats for the spec docker
        [u'blkio_stats', u'precpu_stats', u'network', u'read', u'memory_stats', u'cpu_stats']
        '''
        cli=self.cli
        data=cli.stats(docker_id,stream=False)
        io={}
        mon={}
        # percent %
        
        #cpu
        cpu={}
        cpu['used']=data['cpu_stats'].values()[0]['total_usage']
        cpu['total']=data['cpu_stats']['system_cpu_usage']
        mon['cpu']='%.2f' % (cpu['used']/cpu['total']*100)
        
        #mem
        mem={}
        mem['used']=data['memory_stats']['usage']
        mem['total']=data['memory_stats']['limit']
        mon['mem']='%.2f' % (mem['used']/mem['total']*100)
        
        #net
        mon['net']=data['network']
        
        ##io speed MB
        read=0
        write=0
        total=0
        
        for i in data['blkio_stats']['io_service_bytes_recursive']:
            if i['op']=='Read':
                read=read+i['value']
            elif i['op']=='Write':
               write=write+i['value']
            elif i['op']=='Total':
                total=total+i['value']
    
        io['read']=read/1024/1024
        io['write']=write/1024/1024
        io['total']=total/1024/1024
        mon['io']=io
        
        ##iowait
        iowait={}
        iowait['used']=data['cpu_stats'].values()[0]['total_usage']-data['cpu_stats'].values()[0]['usage_in_usermode']-data['cpu_stats'].values()[0]['usage_in_kernelmode']
        iowait['total']=data['cpu_stats']['system_cpu_usage']
        mon['iowait']='%.2f' % (iowait['used']/iowait['total']*100)
        
        
        return mon



    def top(self,docker_id,ps_args='aux'):
        '''
        docker top for the spec docker
        
        ps -aux
        '''
        cli=self.cli
        return cli.top(docker_id)
    
    def cmd(self,docker_id,cmd):
        '''
        execute command in the spec docker
        print cmd('ea9de93d89ee','df -h')
        '''
        cli=self.cli
        exec_id=cli.exec_create(docker_id, cmd)
        return cli.exec_start(exec_id)
    
    def md5sum(self,input): 
        import hashlib                       
        fmd5 = hashlib.md5(input)  
        return fmd5.hexdigest() 
    
    

class dockerAgent(dockerBase):
    def __init__(self,ipAdd,version,DBconf):
        super(dockerAgent,self).__init__(ipAdd,version)
        self.DBconf=DBconf
        
        import socket
        self.agent_ip=socket.gethostbyname(socket.gethostname())
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        
        engine = create_engine(DBconf)
        session = sessionmaker(bind=engine)
        self.Session=session()
        import socket
        self.agent_ip=socket.gethostbyname(socket.gethostname())
    
    
    
    def agent(self):
        from threading import  Thread

        self.agent_ip='192.168.9.148'
        monitor_list=self.Session.query(monitor.agent_id,monitor.container_id).filter(agent.agent_ip==self.agent_ip,monitor.status==1).distinct()
        cli=dockerAgent(self.ipAdd,self.version,self.DBconf)
        
        
        #print monitor_list
        sys_threadlist=[]
        cmd_threadlist=[]
        for contains in monitor_list:
            
            #print contains
            sys_threadlist.append(
                                  Thread(target=cli.insertSYS,args=(contains.agent_id, contains.container_id)
                                         )
                                  )
            
            cmd_threadlist.append(
                                  Thread(target=cli.insertCMD,args=(contains.agent_id, contains.container_id)
                                         )
                                  )
        for threadsys in sys_threadlist:
            #threadsys.setDaemon(True)
            threadsys.start()
            
        for threadcmd in cmd_threadlist:
            #threadsys.setDaemon(True)
            threadcmd.start()
        for threadsys in sys_threadlist:
            #threadsys.setDaemon(True)
            threadsys.join()
            
        for threadcmd in cmd_threadlist:
            #threadsys.setDaemon(True)
            threadcmd.join()
    
    
    
    def insertSYS(self,agentid,containid):
        '''
        item montier insert
        intial = true if first insert the data
        
        '''
        
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        
        engine = create_engine(self.DBconf)
        session = sessionmaker(bind=engine)
        Session=session()
        
        ip=Session.query(agent.agent_ip).filter(agent.agent_id==agentid).first()
        monitor_list=Session.query(monitor.monitor_id,monitor.type,monitor.items,monitor.interval).filter(monitor.agent_id==agentid,monitor.container_id==containid,monitor.status==1,monitor.type!=10).all()
        
        ipAdd=self.ipAdd
        version=self.version
        data=dockerBase(ipAdd,version).stat(containid)
        result=[]
        for item in monitor_list:
            #print item
            #print Session.query(history_net).filter(history_net.monitor_id==item.monitor_id).first()
            if item.type=='3' and Session.query(history_net).filter(history_net.monitor_id==item.monitor_id).first()==None:
                histnet=history_net(monitor_id=item.monitor_id,
                                    rx_packets=int(data['net']['rx_packets']),
                                    tx_packets=int(data['net']['tx_packets']),
                                    rx_bytes=int(data['net']['rx_bytes']),
                                    tx_bytes=int(data['net']['tx_bytes'])
                                    )
                result.append(histnet)
                #print 'w11'
            elif item.type=='3' :
                predata=Session.query(history_net).filter(history_net.monitor_id==item.monitor_id).order_by(history_net.time.desc()).first()
                histnet=history_net(monitor_id=item.monitor_id,
                                    rx_packets=int(data['net']['rx_packets'])-int(predata.rx_packets),
                                    tx_packets=int(data['net']['tx_packets'])-int(predata.tx_packets),
                                    rx_bytes=int(data['net']['rx_bytes'])-int(predata.rx_bytes),
                                    tx_bytes=int(data['net']['tx_bytes'])-int(predata.tx_bytes)
                                    )
                #print 'qq'
                
                result.append(histnet)
            elif item.type=='1':
                histcpu=history_sys(monitor_id=item.monitor_id,
                                    value=str(data['cpu']))
                result.append(histcpu)
                
            elif item.type=='5':
                histmem=history_sys(monitor_id=item.monitor_id,
                                    value=str(data['mem']))
                result.append(histmem)
            elif item.type=='2':
                histiowait=history_sys(monitor_id=item.monitor_id,
                                       value=str(data['iowait']))
                result.append(histiowait)
            elif item.type=='7':
                histio=history_sys(monitor_id=item.monitor_id,
                                   value=str(data['io']))
                result.append(histio)
            
        Session.add_all(result)
        try:
            Session.commit()
        except:
            Session.rollback()
        
        Session.close()
        
    def insertCMD(self,agentid,containid,):
        '''
        insert route and disk usage
        '''
        
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        data=self.statCMD(agentid, containid)
        #print 'w11'
        engine = create_engine(self.DBconf)
        session = sessionmaker(bind=engine)
        Session=session()
        
        ip=Session.query(agent.agent_ip).filter(agent.agent_id==agentid).first()
        monitor_list=Session.query(monitor.monitor_id,monitor.type,monitor.items,monitor.interval).filter(monitor.agent_id==agentid,monitor.container_id==containid,monitor.status==1,monitor.type!=10).all()
        
        ipAdd=self.ipAdd
        version=self.version
        
        
        result=[]
        for item in monitor_list:
            #print item
            if item.type=='6':
                
                histdf=history_sys(monitor_id=item.monitor_id,
                                    list=str(data['disk']))
                result.append(histdf)       
            elif item.type=='4':
                histroute=history_sys(monitor_id=item.monitor_id,
                                        list=str(data['route']))
                result.append(histroute)
            elif item.type=='8':
                histproc=history_sys(monitor_id=item.monitor_id,
                                        list=str(data['proc']))
                result.append(histproc)
                
            elif item.type=='9':
                histport=history_sys(monitor_id=item.monitor_id,
                                        list=str(data['port']))
                result.append(histport)
        Session.add_all(result)
        try:
            Session.commit()
        except:
            Session.rollback()
        Session.close()
        
    def insertDB_ForMoniterid(self,monitorid,type):
        '''
        get data for the spec monitor and insert to the db
        type:
        
        TODO
        '''
        
    
    
    def getCmd(self,agentid,containid,cmd):
        '''
        base cmd get
        '''
        #ip=self.Session.query(agent.agent_ip).filter(agent.agent_id==agentid).first()
        
        self.cli = docker.Client(base_url=self.ipAdd,version=self.version)
        a=self.cmd(containid, cmd)
        return a
    
    def statCMD(self,agentid,containid):
        '''
        get the information of route and df -h
        '''
        
        mon={}
        #route
        a=self.getCmd(agentid,containid,'route')
        mon['route']=self.md5sum(a)
        
        a=self.getCmd(agentid,containid,'df -h').rstrip('\n').rstrip(' ').splitlines()[1:]
        disk={}

        for i in a:
            #print i.split()
            #print i.split()[1]
            df={}
            df['Size']=i.split()[1]
            df['Used']=i.split()[2]
            df['Avail']=i.split()[3]
            df['UsePercent']=i.split()[4].rstrip('%')
            df['dev']=i.split()[0]
            disk[i.split()[5]]=df

        mon['disk']=disk
        
        #procss
        procl={}

        a=self.getCmd(agentid,containid, 'ps -aux').rstrip('\n').splitlines()[1:]
        for i in a:
            proc={}
            proc['pid']=i.split()[1]
            proc['USER']=i.split()[0]
            proc['%CPU']=i.split()[2]
            proc['%MEM']=i.split()[3]
            proc['VSZ']=i.split()[4]
            proc['RSS']=i.split()[5]
            proc['STAT']=i.split()[7]
            proc['START']=i.split()[8]
            proc['TIME']=i.split()[9]
            procl[' '.join(i.split()[10:])]=proc
        mon['proc']=procl
        
        #port
        portl={}

        a=self.getCmd(agentid,containid, 'netstat -nlptu').rstrip('\n').splitlines()[2:]
        for i in a:
            port={}
            port['Proto']=i.split()[0]
            port['Recv-Q']=i.split()[1]
            port['Send-Q']=i.split()[2]
            port['Foreign Address']=i.split()[4]
            port['State']=i.split()[5]
            port['PID']=i.split()[6]
            portl[i.split()[3]]=port
        
        mon['port']=portl
        
        return mon
    

    def sys_getjson(self):
        '''
        sys item montier
        TODO
        '''





