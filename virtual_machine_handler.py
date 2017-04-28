#!/usr/bin/python

import os
import time
import signal
import json
import subprocess
from hashlib import sha256

from itsdangerous import Signer

SECRET_KEY = '04460359707883037ba53d6fd358f9bccfbb65cfe6e0aef0bbc56e655228'
MIN_TIME_COPY = 300
USER = 'user'
VM_NAME = 'vm.qcow2'
NAME = 'Test Virtual Machine'

os.chdir("/home/user/")

def copyvm(name):
    print "\n\033[32mCopying VM Disk:\033[0m"
    subprocess.call(["rsync","-ah","--progress","--inplace",VM_NAME,name])

def getsession(name):
    pid,_ = subprocess.Popen(["pgrep","--full",name],stdout=subprocess.PIPE).communicate()
    if pid == '':
        return None
    return int(pid.split('\n')[0])

def killsession(name):
    pid = getsession(name)
    if pid==None:
        print "\n\033[31mNo session was running!\033[0m"
    else:
        print "\n\033[31mKilling QEMU instance"
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        for i in range(5):
            pid = getsession(name)
            if pid!=None:
                time.sleep(1)
            else:
                return
        pid = getsession(name)
        if pid!=None:
            print "\n\033[31mQEMU instance will not terminate. SIGKILLing..."
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)



def bootvm(name):
    print "\n\033[32mBooting VM. Please wait... (This may take some time...)\033[0m"
    subprocess.call(["qemu-system-i386",
            "-hda",name,
            "-nographic",
            "-monitor", "/dev/null",
            "-net", "nic,vlan=0",
            "-net", "user,vlan=0",
            "-chardev", "stdio,signal=off,id=serial0",
            "-smp", "cpus=5",
            "-serial", "chardev:serial0",
            "-enable-kvm"])
    



def login():
    print "\033[32mWelcome to the \033[33mCTFd\033[32m VM system\033[0m"
    print
    print "Please enter your team access token to continue (found in the challenge description):"
    print ">>",
    pw = raw_input()
    pw = pw.decode('base64')

    try:
        teamid = str(json.loads(Signer(SECRET_KEY, salt=NAME, digest_method=sha256).unsign(pw))['team'])
    except Exception as e:
        print "\033[31mInvalid password!"
        exit()

    dirname = os.path.join('vms',teamid.replace('/',''))

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    vmname = os.path.join('vms',teamid.replace('/',''),'vm.qcow2')
    meta = os.path.join('vms',teamid.replace('/',''),'meta')
    

    if not os.path.isfile(vmname):
        copyvm(vmname)
        with open(meta,'w') as f:
            f.write(str(int(time.time())))

    while True:
        print "\n\033[33mVM Menu:\033[0m"
        print " 1: Boot VM"
        print " 2: Repair VM"
        print " 3: Kill QEMU Instance"
        print ">>",
        pw = raw_input()
        if pw=='1':
            if getsession(vmname)!=None:
                print "\033[31mYou already have a session running.\033[0m"
                print "Do you want to kill it? [y/n]",
                if raw_input()!='y':
                    exit()
                killsession(vmname)
            bootvm(vmname)
            exit()
        elif pw=='2':
            with open(meta, 'r') as f:
                old = int(f.read())
            if time.time() - old < MIN_TIME_COPY:
                print "\033[31mYou copied too recently. Please wait %u seconds"%int(old + MIN_TIME_COPY - time.time())
            else:
                if getsession(vmname)!=None:
                    print "\033[31mYou currently have a session running.\033[0m"
                    print "Do you want to kill it? [y/n]",
                    if raw_input()!='y':
                        exit()
                    killsession(vmname)
                with open(meta,'w') as f:
                    f.write(str(int(time.time())))
                copyvm(vmname)
        elif pw=='3':
            killsession(vmname)
        else:
            exit()

login()


