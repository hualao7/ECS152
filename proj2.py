import Queue
import random
import math
import sys

class Host:
    def __init__(self,num,backoff):
        self.id = num
        #self.queue = Queue.Queue()
        self.elist = []
        self.waitingForACK = False
        self.T = backoff
        self.origT = backoff
        self.numUnsuc = 1
        self.counter = 0
        #self.eventWaiting = False
        self.timeStartedWaitingforACK = 0
        self.timeWaitingToTransmit = 0
    def addEvent(self,event):
        self.elist.append(event)
        self.elist.sort(key=lambda e: e.time)
    def removeTopEvent(self):
        self.elist.pop(0)

class Event:
    def __init__(self, time, eventType, size, transTime, src, dest):
        self.time = time
        self.type = eventType
        self.size = size
        self.transTime = transTime
        self.src = src
        self.dest = dest
    def __repr__(self):
        return '{} to {} at {}'.format(self.src,self.dest,round(self.time,5))


class Frame:
    def __init__(self, frameType, size, arrivalTime):
        self.type = frameType #Data or ACK
        self.size = size #mu
        self.init = arrivalTime #lambda

class Stats:
    byte = 0
    delay = 0

class g:
    hosts = []
    GEL = []
    time = 0
    arrivalRate = 0 #lambda
    frameSizeRate = 0 #mu
    rate = 11*math.pow(10,6) #11Mbps
    channelBusy = False
    DIFS = 0.0001
    SIFS = 0.00005
    timeout = 0
    frameTransmitting = 0
    timeFinishes = 0

def main():
    if len(sys.argv) != 7:
        print "Usage: proj1.py <arrivalRate> <frameSizeRate> <N:# of host> <T:max backoff> <timeout> <Duration(seconds)>"
        return "Usage: proj1.py <arrivalRate> <frameSizeRate> <N:# of host> <T:max backoff> <timeout> <Duration(seconds)>"

    g.arrivalRate = sys.argv[1]
    g.frameSizeRate = sys.argv[2]
    g.N = int(sys.argv[3])
    T = int(sys.argv[4])
    g.timeout = int(sys.argv[5])
    g.iteration = sys.argv[6]

    print "==============================="
    print "Arrival Rate: ", g.arrivalRate
    print "Frame Size Rate: ", g.frameSizeRate
    print "N: ", g.N
    print "T: ", T
    print "Timeout: ", g.timeout
    print "Duration(seconds): ", g.iteration
    print "==============================="
    
    #Create the host
    #Create first events for each host
    for i in range(g.N):
        tempHost = Host(i,T)
        g.hosts.append(tempHost)
        newEvent = CreateArrivalEvent("Data",i,randomhost(i))
        #tempHost.queue.put(newEvent)
        tempHost.addEvent(newEvent)
        #g.GEL.append(newEvent)
    
    #sortGEL()

    #Begin simulation, 0.01ms per loop
    while True:
        if(g.time > float(g.iteration)): break
        else: g.time += 0.00001
        #print "Time: ",g.time, g.iteration
        #check receiving

        if round(g.timeFinishes,5) == round(g.time,5):
            #printAllHost()            
            #if data: at that time, create ACK 
            eventType = g.frameTransmitting.type
            d = g.frameTransmitting.dest
            s = g.frameTransmitting.src
            g.channelBusy = False
            #keeping stats
            Stats.delay += g.time - g.frameTransmitting.time
            Stats.byte += g.frameTransmitting.size
            if eventType == "Data":
                #print "Data:",s,"to",d,"at",round(g.time,5)
                d = g.frameTransmitting.dest
                s = g.frameTransmitting.src
                newACK = CreateArrivalEvent("ACK",d,s)
                #g.hosts[d].queue.put(newACK)
                g.hosts[d].addEvent(newACK)
            elif eventType == "ACK": #else ACK: reset the variables for sender
                #print "Ack:",s,"to",d,"at",round(g.time,5)
                #g.hosts[i].eventWaiting = False #reset the top event for this host
                g.hosts[d].counter = 0
                g.hosts[d].timeWaitingToTransmit = 0
                g.hosts[d].T = g.hosts[d].origT
                g.hosts[d].numUnsuc = 1
                g.hosts[d].waitingForACK = False
                g.timeFinishes = 0
                g.hosts[d].removeTopEvent() #remove the transmitted data
            
            
        #go through each host and see if they are waiting for ACK
        #send a packet
        #update counter
        for i in range(g.N):
            if g.hosts[i].waitingForACK is False: #only transmit or count down when not waiting for ACK
                if g.hosts[i].elist[0].time <= g.time: #Frame has arrived and waiting to be sent
                    if g.channelBusy is False: #channel is free
                        #print "Host",i,": Channel is free"
                        if g.hosts[i].counter == 0: #counted all the way down
                            #send after DIFS,
                            g.hosts[i].timeWaitingToTransmit += 0.00001

                            if (g.hosts[i].elist[0].type is "Data" and 
                                    g.hosts[i].timeWaitingToTransmit >= g.DIFS) or \
                                    (g.hosts[i].elist[0].type is "ACK" and 
                                    g.hosts[i].timeWaitingToTransmit >= g.SIFS):
                                #print "Host",i,": sending",g.hosts[i].elist[0].type,"to Host",g.hosts[i].elist[0].dest,"at",g.time,
                                #set channel busy and put the frame being sent in g.frameTransmitting
                                g.channelBusy = True
                                g.frameTransmitting = g.hosts[i].elist[0]
                                #Figure out what time it finishes
                                #max(..): because if frame size < 1 channel will always be busy
                                g.timeFinishes = round(g.time,5) + max(round(g.frameTransmitting.transTime,5),0.00001)
                                #print "Finishes at",g.timeFinishes
                                if g.hosts[i].elist[0].type is "Data":
                                    #create new arrival event for the src host
                                    newEvent = CreateArrivalEvent("Data",i,randomhost(i))
                                    g.hosts[i].addEvent(newEvent)
                                    #start waiting for ACK (set waitingForACK to true and set timeStartedW = g.time)
                                    g.hosts[i].timeStartedWaitingForACK = g.time
                                    g.hosts[i].waitingForACK = True
                                else:
                                    g.hosts[i].removeTopEvent() #remove the ACK event
                                g.hosts[i].timeWaitingToTransmit = 0
                        else: #still counting down
                            g.hosts[i].counter -= 1 #count down
                    else: #channel is busy
                        #print "Host",i,": Channel is busy at",g.time
                        g.hosts[i].timeWaitingToTransmit = 0 #reset the wait for DIFS/SIFS
                        if g.hosts[i].counter == 0: #start the counter
                            g.hosts[i].counter = randomBackoff(g.hosts[i].numUnsuc*g.hosts[i].T)
                            print "Host",i,"begins backoff for",g.hosts[i].counter
            else: #waiting for ACK
                #timeout
                if g.hosts[i].timeStartedWaitingforACK+g.timeout == g.time:
                    print "Host",i,"TIMEOUT: send again!"
                    #increment unsuccessful
                    g.hosts[i].numUnsuc += 1
                    #re-send 
                    g.hosts[i].waitingForACK = False

    #finished simulation
    print "*******************************"
    print "Total Bytes:",Stats.byte
    print "Total Delay:",Stats.delay
    print "*******************************"

def printAllHost():
    for i in range(g.N):
        print "Host",i,"[",g.hosts[i].elist,"]"
        
def negativeExpDistTime(rate):
    rand = random.random()
    return ((-1/float(rate))*math.log(1-rand))

def randomBackoff(t):
    return int(round(random.uniform(0,t)))
 
def randomhost(i):
    rand = int(round(random.uniform(0,g.N-1)))
    while rand == i:
        rand = int(round(random.uniform(0,g.N-1)))
    return rand

def CreateArrivalEvent(eventType,senderID,destID):
    if eventType == "ACK":
        size = 64
        eventtime = g.time
    elif eventType == "Data":
        rand2 = negativeExpDistTime(g.frameSizeRate)
        while rand2 > 1:
            rand2 = negativeExpDistTime(g.frameSizeRate)
        size = rand2*1544
        rand = negativeExpDistTime(g.arrivalRate) #this is for arrival
        eventtime = g.time + rand


    transTime = size*8/g.rate
    anEvent = Event(eventtime, eventType, size, transTime, senderID, destID) #new event
    return anEvent

def ProcessArrivalEvent(event):
    #print "ARRIVING: ", event.time
    i = event.src

    #Create receive event that will notify the dest
    #CreateReceiveEvent(event)

    #Create the next arrival event
    newEvent = CreateArrivalEvent("Data",i,randomhost(i))
    #g.hosts[i].queue.put(newEvent)
    g.hosts[i].addEvent(newEvent)


def sortList(elist):
    elist.sort(key=lambda e: e.time)
    
if __name__ == "__main__":
    main()
