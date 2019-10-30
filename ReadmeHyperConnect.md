######################################## Readme Hyperconnect.py #######################################
This script is to be run on hypervisors running qemu in order to resolve potential IP and MAC duplication issues. The script auto-assigns MAC addresses and IP address taking into account the subnets they were created in. 
Steps to run the script: 
1. Ensure that the following libraries are installed on the VMs: 
	- qemu-guest-agent
2. Ensure that the python library is installed on the hypervisor: 
	- xml.etree.ElementTree
	- ipaddress
	- pexpect
	
3. Ensure that the Hypervisors and Domains that you are managing has passwordless SSH access. Follow: https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/
Note: Ensure that the passwordless login for the guest domains are set up for the root account. 

4. Ensure that all the management IP addresses are on eth0 or the ip addresses on eth0 are reachable to manage remotely through the script.

Author: 
Mukul Manikandan (mmanika@ncsu.edu)

######################################## Readme Hyperconnect.py #######################################
