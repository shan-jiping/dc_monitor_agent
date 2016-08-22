# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from libs.Base import dockerM,dockerBase,dockerAgent
from model import *
import docker

              
                                  

##global declare_namespace
##global declare_namespace
ipAdd='tcp://192.168.9.148:6732'
DBconf='mysql://w11:w11@192.168.8.22:3306/dockerM'
version='1.20'

'''
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
        
engine = create_engine(DBconf)
session = sessionmaker(bind=engine)
Session=session()

for key,value in Session.query(setting.key,setting.value1).all():
    key=value
    '''

#print dockerBase(ipAdd,version).version2()

'''
初始化基础模板
'''
#dockerM(DBconf).BaseTemplate()
'''
添加主机和docker
'''
dockerM(DBconf).add_agent('192.168.9.148', '6732')
#dockerM(DBconf).monitor_agent()
'''
第一次收集信息
'''
#dockerAgent(DBconf).insertSYS(1, '1288b7c2af65',True)
#dockerAgent(DBconf).insertCMD(1, '1288b7c2af65')
'''
以后收集信息
'''
#dockerAgent(DBconf).insertSYS(1, '1288b7c2af65')
#dockerAgent(DBconf).insertCMD(1, '1288b7c2af65')

