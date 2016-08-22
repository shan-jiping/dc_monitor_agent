import tornado.ioloop
import tornado.web
from libs.Base import *
from libs.model import *
from time import sleep,time
import os
import logging,logging.config
import ConfigParser

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("I am OK!")
    
    
def make_app():
    return tornado.web.Application([
                                    (r"/", MainHandler),
                                    ])
def main():
    while True:
        try:
            dockerAgent(ipAdd,version,DBconf).agent()
            agent_logger.log(20,'finish get data')
            sleep(interval)
        except Exception,e:
            agent_logger.log(50,e)
            break

    
if __name__ == "__main__":
    LOGGING_CONF_LOG ='./conf/logging.conf'
    logging.config.fileConfig(LOGGING_CONF_LOG)
    agent_logger = logging.getLogger('agent')
    cf = ConfigParser.ConfigParser()
    cf.read("./conf/init.conf")
    ipAdd=cf.get("common", "ipAdd").strip('\'') 
    version=cf.get("common", "version").strip('\'') 
    DBconf=cf.get("common", "DBconf").strip('\'')
    port=int(cf.get("common", "port")) 
    interval=float(cf.get("common", "interval"))  
    app = make_app()
    app.listen(port)
    agent_logger.log(20,'server start')
    tornado.ioloop.IOLoop.current().run_sync(main)