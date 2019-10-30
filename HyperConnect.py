from __future__ import print_function
import sys
import libvirt
import xml.etree.ElementTree as ET
import ipaddress
from pexpect import pxssh

def ConnectToHypervisor(ip):
	conn = libvirt.open('qemu+ssh://'+ip+'/system')
	if conn == None:
		print('Failed to open connection to qemu+tls://host2/system', file=sys.stderr)
		exit(1)

	#DomList=conn.listDomainsID()
	DomList=[114,130,132]

	ifaces={}
	for i in DomList:
		dom = conn.lookupByID(i)
		ifaces.update({str(i):dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT,0)})

	print (ifaces)

	#Check for MAC address duplication:

	MACs={}
	MACAddressPool=[]
	for x in ifaces.keys():
		MACs[x]=[]

	for i in ifaces.keys():
		for j in ifaces[i].keys():
			if 'eth' in j:
				MACs[i].append({j:ifaces[i][j]['hwaddr']})
				MACAddressPool.append(ifaces[i][j]['hwaddr'])
				#print (conn.interfaceLookupByMACString(ifaces[i][j]['hwaddr']).name())

	print (MACs)
		
	for i in MACs.keys():
		#print (i)
		for j in MACs[i]:
			#print(j)
			MACAddressPool.remove(j.items()[0][1])
			if j.items()[0][1] in MACAddressPool:
				#Generate new MAC address
				#Assign the MAC address to the VM
				newMac=j.items()[0][1][:-2]+hex((int(j.items()[0][1][-2:],16)+1)%255).lstrip("0x").zfill(2)
				while newMac in MACAddressPool: 
					newMac=newMac[:-2]+hex((int(newMac[-2:],16)+1)%255).lstrip("0x").zfill(2)
				
				dom = conn.lookupByID(int(i))
				raw_xml = dom.XMLDesc(0)
				root = ET.fromstring(raw_xml)
				devices=root.find('devices')
				interfaces=devices.findall('interface')
				for interface in interfaces: 
					mac=interface.find('mac')
					if mac.attrib['address'].strip() == j.items()[0][1].strip():
						#print (mac.attrib['address'])
						mac.attrib['address']=newMac
						#print (mac.attrib['address'])
						#print (ET.tostring(root))
						conn.defineXML(ET.tostring(root))
						dom.shutdown()
						while dom.isActive():
							i=0
							i=i+1
						conn.createXML(ET.tostring(root))
						while not dom.isActive():
							i=0
							i=i+1


	#Check for IP address duplication:

	IPs={}
	IPPool=[]
	for x in ifaces.keys():
		IPs[x]=[]
	ManagementIP={}
	for i in ifaces.keys():
		for j in ifaces[i].keys():
			if 'eth0' in j: 
				ManagementIP[i]=(ifaces[i][j]['addrs'][0]['addr'])
			if 'eth' in j:
				if ifaces[i][j]['addrs'] is not None and ifaces[i][j]['addrs'][0]['type']==0:
					IPs[i].append({j:ifaces[i][j]['addrs'][0]['addr']})
					IPPool.append(ifaces[i][j]['addrs'][0]['addr'])


	print (IPs)
	#print(ManagementIP)


	for i in IPs.keys():
		#print (i)
		for j in IPs[i]:
			#print(j)
			IPPool.remove(j.items()[0][1])
			if j.items()[0][1] in IPPool:
				#Generate new IP address
				#Assign the IP address to the VM
				#print (i,j)
				newIP=ipaddress.ip_address(unicode(j.items()[0][1],'utf-8'))+1%ifaces[i][j.keys()[0]]['addrs'][0]['prefix']
				while newIP in IPPool: 
					newIP=newIP+1%255
				
				print ("Your IP address of VM with ID {} is conflicting with an IP of another VM. Please change the IP to {} for this domain.".format(i, newIP))
				#Implement logic to ssh into management device and change the IP address.
				try:
					s=pxssh.pxssh()
					s.login(ManagementIP[i], 'root')
					s.sendline('ip link set dev '+j.items()[0][0]+' down')
					s.sendline('ip addr del '+j.items()[0][1]+' dev '+j.items()[0][0])
					s.sendline('ip addr add '+str(newIP)+'/24 dev '+j.items()[0][0])   
					s.sendline('ip link set dev '+j.items()[0][0]+' up')
					s.logout()
				except pxssh.ExceptionPxssh as e:
					print (e)
	conn.close()
	print("\n\n\n")

print("Enter the IP addresses of the Hypervisors you would like to run the program on separated by spaces:\n")
x=raw_input("Input:")
x=x.split()

for i in x: 
	ConnectToHypervisor(i)
