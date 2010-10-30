'''
Created on 03.05.2010

@author: toby
'''

import os, sys
from re import *    
from subprocess import call
from time import strftime

class containerDefault(object):
    '''
    classdocs
    '''
    def __init__(self, domain, env):
        self.env = env
        self.domain = domain
        
        self.vars = {}
        self.file = None
        self.vhostpath = None
        self.fileprefix = None
        self.reloadcommand = None
        self.template = None
        self.vars['logpath'] = {'access': None, 'error': None}
        self.parsedTemplate = None
        
        self.setVars()
        
    def setVars(self):
        self.template = self.env.config.get('container' + self.myName + 'template')
        self.vhostpath = os.path.abspath(self.env.config.get('container' + self.myName + 'vhostpath'))
        self.fileprefix = self.env.config.get('container' + self.myName + 'fileprefix')
        self.ipandportprefix = self.env.config.get('container' + self.myName + 'ipandportprefix')
        self.reloadcommand = self.env.config.get('container' + self.myName + 'reloadcommand')
        
        self.vars['logpath'] = self.env.config.get('container' + self.myName + 'logPath')
        self.vars.update(self.domain.vhostContainer.vhost)
        self.vars.update(self.domain.domain)
        self.vars.update(self.domain.user.user)
        
        self.file =  os.path.abspath(self.vhostpath + '/' + self.fileprefix + '_' + self.domain.domainID + '_' + self.domain.get("domainname") + '.conf')
    
    def createDomain(self):
        self.parse()
        self.createPath()
        self.writeFile()
    
    #update is nearly the same as create
    def updateDomain(self):
        self.deleteDomain()
        self.createPath()
        self.create()
                
    def deleteDomain(self):
        self.getFilePath()
        
        if self.file <> False:
            os.remove(self.file)
            self.reloadServer()
            
    def parse(self):    
        try:
            from Cheetah.Template import Template
        except ImportError:
            self.env.logger.append("Cheetah-Template seems not to be installed! Please install python-cheetah")
            raise
        self.parsedTemplate = Template(self.template, searchList=[self.vars])
        
    def getFilePath(self):
        if os.access(self.file, os.F_OK):
            return self.file
        else:
            #maybe renamed, domainname is wrong?
            files = os.listdir(self.vhostpath)
            
            for file in files:
                if search(self.fileprefix + '_' + self.domain.domainID + '_.*', file) <> None:
                    return self.vhostpath + '/' + file
                
        return False
    
    def createPath(self):
        path = os.path.normcase(self.domain.get('documentroot'))
        if os.path.exists(path) == False:
            paths = path.split(os.sep)
            wpath = os.sep
            for p in paths:
                wpath += p + os.sep
                
                if os.path.exists(wpath) == False:
                    os.mkdir(wpath)
                    gid = int(self.domain.user.get('guid'))
                    os.chown(wpath, gid, gid)
        
    def writeFile(self):
        if self.parsedTemplate <> None:
            f = file(self.file, 'w')
            f.write('# autogenerated by WCP on ' + strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write("# DO NOT CHANGE MANUALLY, ALL CHANGES WILL BE LOST NEXT TIME THIS FILE IS GENERATED!\n")
            f.write(str(self.parsedTemplate))
            f.close()
            
    def finishContainer(self):
        self.writeIPandPort()    
        self.reloadServer()
        
    def writeIPandPort(self):
        ipAndPort = ""
        if self.domain.vhostContainer.get('addListenStatement'):
            ipAndPort += "Listen " + str(self.domain.vhostContainer.get('ipAddress')) + ":" + str(self.domain.vhostContainer.get('port')) + "\n"
            
        if self.domain.vhostContainer.get('addNameStatement'):
            ipAndPort += "NameVirtualHost " + str(self.domain.vhostContainer.get('ipAddress')) + ":" + str(self.domain.vhostContainer.get('port')) + "\n"
            
        if ipAndPort:
            f = file(os.path.abspath(self.vhostpath + '/' + self.ipandportprefix + '_' + str(self.domain.vhostContainer.get('ipAddress')) + "." + str(self.domain.vhostContainer.get('port')) + '.conf'), 'w')
            f.write(ipAndPort)
            f.close()
            
    def reloadServer(self):
        try:
            retcode = call(self.reloadcommand, shell=True)
            if retcode <> 0:
                self.env.logger.append("restart " + self.myName + " failed")
                return False
            else:
                self.env.logger.append("restart " + self.myName + " ok")
                return True
        except OSError, e:
            elf.env.logger.append("restart " + self.myName + " failed")
            return False