from sqlalchemy import create_engine
engine = create_engine('mysql://w11:w11@192.168.8.22:3306/dockerM')


from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey,text
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR,INTEGER
        

class monitor(Base):
    '''
    main table
    '''
    __tablename__ = 'monitor'
    monitor_id = Column(INTEGER, primary_key=True)
    agent_id=Column(Integer, ForeignKey('agent.agent_id'))
    user_id= Column(INTEGER)
    docker_id= Column(VARCHAR(32))
    container_id= Column(VARCHAR(32))
    threshold=Column(VARCHAR(32))
    result_type=Column(VARCHAR(32))
    type=Column(VARCHAR(32))
    items=Column(VARCHAR(60))
    domain=Column(VARCHAR(32))
    status=Column(VARCHAR(6))
    createtime=Column(TIMESTAMP, server_default = func.now())
    updatetime=Column(TIMESTAMP, server_onupdate=text('CURRENT_TIMESTAMP'))
    interval=Column(INTEGER)
    email=Column(VARCHAR(32))
    
    #FK
    agent = relationship("agent",)
    
    def __repr__(self):
        return "<Monitor(monitorid='%s', agentid='%s', dockerid='%s', container_id='%s')>" % (self.monitor_id, self.agent_id, self.docker_id,self.container_id)
    
    
    
class agent(Base):
    '''
    agent branch
    '''
    __tablename__ = 'agent'
    agent_id=Column(INTEGER, primary_key=True)
    agent_ip= Column(VARCHAR(32))
    agent_hostname= Column(VARCHAR(32))
    version= Column(VARCHAR(32))
    salt_version= Column(VARCHAR(32))
    docker_version=Column(VARCHAR(80))
    port=Column(INTEGER)
    
    
    #FK
    monitor = relationship("monitor",)
    
    def __repr__(self):
        return "<agent(agentid='%s', agentip='%s')>" % (self.agent_id, self.agent_ip)
    
    
class agent_monitor(Base):
    __tablename__ = 'agent_monitor'
    id=Column(INTEGER, primary_key=True)
    agent_id=Column(Integer, ForeignKey('agent.agent_id'))
    docker_id= Column(VARCHAR(32))
    container_id= Column(VARCHAR(32))
    type=Column(VARCHAR(6))
    items=Column(VARCHAR(32))
    threshold=Column(VARCHAR(32))
    status=Column(VARCHAR(6))
    interval=Column(INTEGER)
    
    #FK
    agent = relationship("agent",)
    
    def __repr__(self):
        return "<agent_monitor(agentid='%s', dockerid='%s',containid='%s')>" % (self.agent_id, self.docker_id,self.container_id)
    
    
class alert(Base):
    __tablename__ = 'alert'
    alert_id=Column(INTEGER, primary_key=True)
    agent_id=Column(Integer, ForeignKey('agent.agent_id'))
    docker_id= Column(VARCHAR(32))
    alters=Column(INTEGER)
    times=Column(TIMESTAMP, server_default = func.now())
    alert_email=Column(VARCHAR(32))
    content=Column(TEXT)

    
    #FK
    agent = relationship("agent",)
    
    def __repr__(self):
        return "<alert(alertid='%s', agentid='%s',dockerid='%s',alert_email='%s')>" % (self.alert_id,self.agent_id ,self.docker_id,self.alert_email)
    
    
    
    

###HISTORY TABLE
class history_net(Base):
    __tablename__ = 'history_net'
    id=Column(INTEGER, primary_key=True)
    monitor_id=Column(Integer, ForeignKey('monitor.monitor_id'))
    rx_packets= Column(INTEGER)
    tx_packets= Column(INTEGER)
    rx_bytes= Column(INTEGER)
    tx_bytes= Column(INTEGER)
    time=Column(TIMESTAMP, server_default = func.now())


    
    #FK
    monitor = relationship("monitor",)
    
    def __repr__(self):
        return "<his_net(monitorid='%s', value='%s',threshold='%s',times='%s')>" % (self.monitor_id,self.value ,self.threshold,self.time)
    
    
class history_sys(Base):
    __tablename__ = 'history_sys'
    id=Column(INTEGER, primary_key=True)
    monitor_id=Column(Integer, ForeignKey('monitor.monitor_id'))
    value= Column(VARCHAR(600))
    list=Column(BLOB)
    threshold=Column(VARCHAR(600))
    time=Column(TIMESTAMP, server_default = func.now())


    
    #FK
    monitor = relationship("monitor",)
    
    def __repr__(self):
        return "<his_sys(monitorid='%s', value='%s',threshold='%s',times='%s')>" % (self.monitor_id,self.value ,self.threshold,self.time)
    
class history_ser(Base):
    __tablename__ = 'history_ser'
    id=Column(INTEGER, primary_key=True)
    monitor_id=Column(Integer, ForeignKey('monitor.monitor_id'))
    value= Column(VARCHAR(600))
    threshold=Column(VARCHAR(600))
    time=Column(TIMESTAMP, server_default = func.now())


    
    #FK
    monitor = relationship("monitor",)
    
    def __repr__(self):
        return "<his_ser(monitorid='%s', value='%s',threshold='%s',times='%s')>" % (self.monitor_id,self.value ,self.threshold,self.time)
    

class setting(Base):
    __tablename__ = 'setting'
    id=Column(INTEGER, primary_key=True)
    key=Column(VARCHAR(32))
    value1= Column(VARCHAR(60))
    value2= Column(VARCHAR(60))
    value3= Column(VARCHAR(60))
    value4= Column(VARCHAR(60))
    value5= Column(VARCHAR(60))
    
class template(Base):
    __tablename__ = 'template'
    template_id=Column(INTEGER, primary_key=True)
    type=Column(VARCHAR(32))
    items= Column(VARCHAR(60))
    threshold= Column(VARCHAR(60))
    interval= Column(INTEGER)


###initail table metadata
#Base.metadata.drop_all(engine)
#Base.metadata.create_all(engine)




