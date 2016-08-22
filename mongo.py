
ipAdd='tcp://10.10.20.190:235'
version='1.20'


import docker
import uuid,re,time




class cluster(object):
    def __init__(self,ipAdd,version,mem_limit='1G',memswap_limit=-1,shm_size='1G',cpu_period=0):
        '''
        
        '''
        self.cli = docker.Client(base_url=ipAdd,version=version)
        self.mem_limit=mem_limit
        self.memswap_limit=memswap_limit
        self.shm_size=shm_size
        self.cpu_period=cpu_period
        
    def __cmd__(self,docker_id,cmd):
        '''
        execute command in the spec docker
        print cmd('ea9de93d89ee','df -h')
        '''
        cli=self.cli
        exec_id=cli.exec_create(docker_id, cmd)
        return cli.exec_start(exec_id)
    
    def __run__(self,uname,image,cmd,lports=None):
        print cmd
        container = self.cli.create_container(image=image, command=cmd,name=uname,detach=True,tty=True,volumes=['/data:/data/mongouname%s' % uuid.uuid4()],
                                             host_config=self.cli.create_host_config(mem_limit='1G',memswap_limit=-1,shm_size='1G',cpu_period=0,port_bindings=lports))
        self.cli.start(container=container.get('Id'))
        return container
    
    def __getip__(self,containid,eth='eth0'):
        ethre=re.compile('inet (\d+.\d+.\d+.\d+)/[\w\W]+ scope global %s' % (eth))
        a=self.__cmd__(containid, 'ip -f inet add')
        for w in a.splitlines():
            #print ethre.search(w.strip(' '))
            if ethre.search(w.strip(' ')):
                ip=str(ethre.match(w.strip(' ')).groups(1)[0])
        return ip
    
    def mongo(self,instance,replicat=2,nums=2,controls=3,mongos=1,abitary=1,maxmem='15M',eth='eth0'):
        
        ##mongd 
        mongo={}
        log={}
        ip={}
        for rep in range(replicat):
            
            
            for num in range(nums):
                r=str(rep)+str(num)
                containid=self.__run__('r%s-mongod-%s' % (r,instance) ,'tkx:centos7',
                                       '/usr/bin/mongod --dbpath /data/mongo --port 27017  --replSet r%s --shardsvr --cacheSize=%s --pidfilepath /data/mongo/mongo.pid' % (rep,maxmem))
                containid['type']='mongod r%s' % r
                mongo['mongod r%s' % r]=containid
                docker_id=containid['Id']
                ip['mongod r%s' % r]=self.__getip__(docker_id, eth)
            for abi in range(abitary):
                r=str(rep)+str(abi)
                containid=self.__run__('a%s-abitary-%s' % (r,instance) ,'tkx:centos7',
                                       '/usr/bin/mongod --dbpath /data/mongo --port 27017  --replSet r%s --shardsvr --cacheSize=%s  --pidfilepath /data/mongo/mongo.pid' % (rep,maxmem))
                containid['type']='abitary r%s' % r
                mongo['abitary r%s' % r]=containid
                docker_id=containid['Id']
                ip['abitary r%s' % r]=self.__getip__(docker_id, eth)
            
                
             
            #print mongo
            #print ip  
            #ip={'mongod r00': '172.17.1.168', 'mongod r01': '172.17.1.169', 'abitary r00': '172.17.1.170'}
            #mongo={'mongod r00': {'type': 'mongod r00', u'Id': u'635246b65797ee359e23ff6700ec39e6fc2ea5c24c6e8b0aa8e9364d9e424cd0', u'Warnings': None}, 'mongod r01': {'type': 'mongod r01', u'Id': u'60d6c820c4e6712c8477686f3dce1ad77067a160425fb0062e51a88a8b6a8f2b', u'Warnings': None}, 'abitary r00': {'type': 'abitary r00', u'Id': u'0aff291463f1733cc18339a89b1d48bd962270a1f08c84ce9f5ce18782517e51', u'Warnings': None}}
            primaryid=mongo['mongod r%s0' % rep]['Id']
            print primaryid
            self.__cmd__(primaryid, 'mongo --eval \'rs.initiate()\'')
            time.sleep(20)
            
            for i in range(1,nums):
                secendaryip=ip['mongod r%s%s' % (rep,i)]
                #print secendaryip
                self.__cmd__(primaryid, 'mongo --eval \'rs.add(\"%s:27017\")\'' % secendaryip)
                
            primaryip=ip['mongod r%s0' % rep]
            self.__cmd__(primaryid, 'mongo --eval \'cfg = rs.conf();cfg.members[0].host = \"%s:27017\";rs.reconfig(cfg)\'' % primaryip)
            
            for i in range(abitary):
                arbitaryip=ip['abitary r%s%s' % (rep,i)]
                #print arbitaryip
                self.__cmd__(primaryid, 'mongo --eval \'rs.addArb(\"%s:27017\")\'' % arbitaryip)
                
            
         
        #mongo control
        cip=[]
        
        for rep in range(controls):
                
            containid=self.__run__('c%s-mongod-%s' % (rep,instance) ,'tkx:centos7'
                                   ,'/usr/bin/mongod --dbpath /data/mongo  --configsvr --port 27017')
            containid['type']='control %s' % rep
            mongo['control %s' % rep]=containid
            docker_id=containid['Id']
            ip['control %s' % rep]=self.__getip__(docker_id, eth)
            cip.append(ip['control %s' % rep])
        #print mongo
        #print ip
            
            
               
        for go in range(mongos):

            #print '/usr/bin/mongos --configdb %s:27017' % (':27017,'.join(cip))               
            containid=self.__run__('mongos%s-%s' % (go,instance) ,'tkx:centos7',
                                   '/usr/bin/mongos --configdb %s:27017' %
                                   (':27017,'.join(cip)))
            containid['type']='mongos %s' % go
            mongo['mongos %s' % go]=containid
            docker_id=containid['Id']
            ip['mongos %s' % rep]=self.__getip__(docker_id, eth)
            
        time.sleep(20)    
        for rep in range(replicat):
            rip=[]
            for num in range(nums):
                r=str(rep)+str(num)
                rip.append(ip['mongod r%s' % r])
            pmongosid=mongo['mongos 0']['Id']
            print pmongosid
            print 'mongo --eval \'sh.addShard(\"r%s/%s:27017\")  \'' % (rep,':27017,'.join(rip))    
            print self.__cmd__(pmongosid, 'mongo --eval \'sh.addShard(\"r%s/%s:27017\")  \'' % (rep,':27017,'.join(rip)))
            

        return mongo
        
    def mysql(self,instance,node=2,cnf=None,eth='eth0',maxcache='0G',innobuffer='1G',innoinstance=2):
        mysql={}
        log={}
        ip={}
        
        name='mysql-%s-master' % (instance)
        containid=self.__run__(name ,'pxc:centos71',
                               '/usr/sbin/mysqld --basedir=/usr --user=mysql --wsrep-new-cluster  --innodb-flush-method=O_DSYNC --wsrep-node-name=%s --innodb-buffer-pool-size=%s --innodb-buffer-pool-instances=%s --key-buffer-size=%s' 
                               % (name,innobuffer,innoinstance,maxcache))
        containid['type']='master'
        mysql[name]=containid
        docker_id=containid['Id']
        ip[name]=self.__getip__(docker_id, eth)
        port=3307
        for rep in range(1,node):
            name='mysql-%s-slave%s' % (instance,rep)
            containid=self.__run__(name ,'pxc:centos71',
                                       '/usr/sbin/mysqld --basedir=/usr --user=mysql --wsrep-node-name=%s --innodb-flush-method=O_DSYNC --wsrep_cluster_address=gcomm://%s --innodb-buffer-pool-size=%s --innodb-buffer-pool-instances=%s --key-buffer-size=%s' 
                                       % (name,ip['mysql-%s-master' % (instance)],innobuffer,innoinstance,maxcache))
            containid['type']='slave'
            mysql[name]=containid
            docker_id=containid['Id']
            ip[name]=self.__getip__(docker_id, eth)
            port=port+1
        return mysql    
            

print cluster(ipAdd,version).mongo('w11',replicat=2,controls=3)
print cluster(ipAdd,version).mysql('w11',node=3)
print "OK"