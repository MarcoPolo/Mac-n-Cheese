
import os, sys, time, subprocess

#make sure to change this to your interface!
iface='eth8'

#find the mac address and ip domain of interface
def findLocalNetworkInfo():
    sout=subprocess.check_output('ifconfig',shell=True)
    sout=sout.split('\n')

    ifaceIndex = -1
    for i in range(len(sout)):
        if iface in sout[i]:
            ifaceIndex=i
            break
            
    macIndex = sout[ifaceIndex].find('HWaddr')+7  #there are 6 characters in hwaddr and a space before the mac address shows up
    systemMac = sout[ifaceIndex][macIndex:-2] #there is a leading space, get rid of it

    ipDomainIndex = sout[ifaceIndex+1].find('inet addr:')+10 #10 is the no of chars in inetaddr: the +1 is because the ip address is located on the line below HWaddr
    ipDomainEndIndex = sout[ifaceIndex+1].find('Bcast')-2 #2 is because there are 2 spaces before the end of the ip

    ipDomain = sout[ifaceIndex+1][ipDomainIndex:ipDomainEndIndex] #store the ip addr
    ipDomainEndIndex=ipDomain.rfind('.') #find the last period in the the ip addr
    ipDomain = ipDomain[0:ipDomainEndIndex] + '.*' #format the ip domain like 192.168.1.*

    print 'using the interface', iface
    print 'found the ip domain to be ', ipDomain
    print 'found the system mac address to be ', systemMac
    netInfo = {'ipDomain':ipDomain,'systemMac':systemMac}
    return netInfo

def startNmap(ipDomain):
    nmap = subprocess.Popen(['nmap','-sP',ipDomain],stdout=subprocess.PIPE) #start the nmap process
    return nmap

def listenToArp():
    arpTable = subprocess.Popen(['arp','-a'],stdout=subprocess.PIPE) #start the nmap process
    return arpTable

def populateMacAddress(netInfo):
    nmap = startNmap(netInfo['ipDomain'])
    arpTable = listenToArp()
    i=0
    m=1
    while arpTable.poll() is None:
        print 'Waiting on the arp table to finish building'
        i+=1
        time.sleep(10)
        if i>5:
            print m, "minute(s) have passed and we are still building..."
            m+=1
            i=0;

    arpCache = arpTable.stdout.read()
    arpCache = arpCache.split('\n')
    validMAClist = []
    for row in arpCache:
        if '<incomplete>' not in row:
            validMAClist.append(row)

    print 'validmac list is ', validMAClist
    print 'arpcache is',arpCache
    for i in range(len(validMAClist)):
        startIndex = validMAClist[i].find('at')+3 # 2 chars and a space
        endIndex = startIndex+17
        validMAClist[i]=validMAClist[i][startIndex:endIndex]
    try:
        validMAClist.remove(netInfo['systemMac'])    #remove the system mac address from list
    except:
        pass
    print 'the macs that are valid are:', validMAClist
    return validMAClist

def resetMAC():
    netInfo=findLocalNetworkInfo()

    validMAClist = populateMacAddress(netInfo)

    for mac in validMAClist:
        print 'Okay we are going to try', mac, 'tell me if it works'
        subprocess.call('ifconfig '+iface+' down', shell=True)
        subprocess.call('ifconfig '+iface+' hw ether ' + mac, shell=True)
        subprocess.call('ifconfig '+iface+' up', shell=True)
        diditwork = raw_input('I changed your mac address, are you connected? (no will change your mac address again, q will quit the program and restore your original mac address)(q/n)')
        if diditwork=='q':
            print 'Have nice day :)'
            subprocess.call('ifconfig '+iface+' down', shell=True)
            subprocess.call('ifconfig '+iface+' hw ether ' + netInfo['systemMac'], shell=True)
            subprocess.call('ifconfig '+iface+' up', shell=True)
            break

user=subprocess.check_output('whoami',shell=True)
if "root" not in user:
    print "got r00t? - I need root to change your mac address!"
    sys.exit()
else:
    resetMAC()
