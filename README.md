# CTFd Virtual Machine Plugin 

This [CTFd](https://github.com/CTFd/CTFd) plugin changes the default list scoreboard into a "matrix" scoreboard.
A matrix scoreboard shows what challenges teams have solved, as well as their place and score.

## Install

### On CTFd
To install, copy the contents of the CTFd director into your local CTFd directory.
Add a `VM_KEY` entry to the config.py file (This will be used to sign the requests)

### On the VM server
Change the constant variables in the `virtual_machine_handler.py` file to match with the username and path you want to use.

Create a `vms` directory in this path.

Copy your virtual machine into the same directory and change the variable in the script.

Set the user's login shell to be `/path/to/virtual_machine_handler.py
