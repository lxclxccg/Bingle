import os, sys, subprocess, tempfile, time
from BackGround import models
import logging
import time
import pexpect
log = logging.getLogger("collect")


def getdebugger(ctype):
    if ctype == "python":
        return pythondebuggers["python"]

class debugger():
    code = ""
    codetype = "python"
    stdin = ""
    stdout = ""
    action =""
    def __init__(self, ctype, c, s):
        self.code = c
        self.codetype = ctype
        self.stdin = s
    def startdebug(self):
        pass
    def stepinto(self):
        pass
    def stepover(self):
        pass
    def stop(self):
        pass


class pythondebugger(debugger):

    process = None
    def __init__(self):
        debugger.__init__(self, "python", "", "")

    def startdebug(self, c, s):
        self.code = c
        self.stdin = s
        result = False
        appresult = ""
        pdbresult = ""
        try:
            TempFile = tempfile.mkdtemp(suffix='_test', prefix='python_') 
            FileNum = "%d.py" % int(time.time() * 1000) 
            fpath = os.path.join(TempFile, FileNum) 
            with open(fpath, 'w', encoding='utf-8') as f: 
                f.write(self.code) 
            #self.process = subprocess.Popen([sys.executable,"-m","pdb" ,fpath,self.stdin],stdin = subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,bufsize=1)
            #self.process.wait()
            #char = self.process.stdout.read()
            
            
            
            
            self.process = pexpect.spawn(sys.executable,["-m","pdb" ,fpath,self.stdin],encoding='utf-8')
            ret = self.process.expect('\(Pdb\)')
            if ret >= 0:
                r = self.process.before.strip()
                r = r.replace('\x07','').replace(self.process.args[3].decode(),'').replace('<module>()','')
                r = r[0:r.find('->')]
                pdbresult = r[r.find('>')+1:].replace('(','').replace(')','').strip()
                result = True
        except Exception as e:
            result = False
        return result, appresult, pdbresult    

    def stepover(self):
        result = False
        appresult = ""
        pdbresult = ""
        try:
            self.process.sendline('n')
            ret = self.process.expect('\(Pdb\)')
            r = self.process.before.strip()
            log.info(r)
            if (r.find('<module>()->None') <= 0):
                r = r.replace('\x07','').replace(self.process.args[3].decode(),'').replace('<module>()','')
                r = r[0:r.find('->')]
                r = r[r.find('\r\n') + 2:].strip()
                appresult = r[0:r.find('>')].replace('--Call--\r\n','')
                r = r[r.find('>') + 1:].strip()
                pdbresult = r[r.find('(')+1:r.find(')')].strip()
                if (appresult.find('--Return--')>=0):
                    return self.stepover()
            else:
                pdbresult = "end"
                appresult = ""
                self.process.close()
            result = True
        except:
            result = False
        return result, appresult, pdbresult

    def stepinto(self):
        result = False
        appresult = ""
        pdbresult = ""
        try:
            self.process.sendline('s')
            ret = self.process.expect('\(Pdb\)')
            if (len(self.process.buffer) > 0):
                log.info(self.process.before)
                log.info(self.process.after)
                log.info(self.process.buffer)
                self.process.buffer = ''
            else:
                log.info(self.process.before)
            r = self.process.before.strip()
            #log.info(r)

            #分离应用输出和PDB输出
            index = r.find('> ' + self.process.args[3].decode())  #index之前基本上为应用输出，之后为PDB输出
            
            if (r.find('> <string>(1)<module>()->None') <= 0):
                r = r.replace('\x07','').replace(self.process.args[3].decode(),'').replace('<module>()','')
                r = r[0:r.find('->')]
                r = r[r.find('\r\n') + 2:].strip()
                appresult = r[0:r.find('>')].replace('--Call--\r\n','')
                r = r[r.find('>') + 1:].strip()
                pdbresult = r[r.find('(')+1:r.find(')')].strip()
                if (appresult.find('--Return--')>=0):
                    return self.stepinto()
            else:
                pdbresult = "end"
                appresult = ""
                self.process.close()
            result = True
        except Exception as e:
            result = False
        
        return result, appresult, pdbresult

    def stop(self):
        result = False
        appresult = ""
        pdbresult = ""
        try:
            self.process.terminate()
            result = True
            
        except:
            result = False
        
        return result, appresult, pdbresult
        

pythondebuggers = {"python":pythondebugger()}
