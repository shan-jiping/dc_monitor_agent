from  libs.Base import dockerAgent
from model import *

ipAdd='tcp://192.168.9.148:6732'
DBconf='mysql://w11:w11@192.168.8.22:3306/dockerM'
version='1.20'


dockerAgent(ipAdd,version,DBconf).agent()
