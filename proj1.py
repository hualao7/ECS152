import Queue
import random
import math
import sys

class Event:
    def __init__(self, time, eventType, serviceTime=0):
        self.time = time
        self.eventType = eventType
        self.serviceTime = serviceTime
    def __repr__(self):
        return '{}: {}'.format(self.eventType,self.time)

class Packet:
    def __init__(self, departTime):
        self.departTime = departTime

class Stats:
    dropped = 0
    meanLength = []
    busy = 0

def main():
    global length
    global time
    global arrivalRate
    global serviceRate
    global bufferQueue
    global GEL
    global MAXBUFFER
    length = 0 #initialize queue length to 0
    time = 0 #initialize time to 0

    if len(sys.argv) != 5:
        print "Usage: proj1.py <arrivalRate> <serviceRate> <MAXBUFFER> <# iter>"
        return "Usage: proj1.py <arrivalRate> <serviceRate> <MAXBUFFER> <# iter>"

    arrivalRate = sys.argv[1]
    serviceRate = sys.argv[2]
    MAXBUFFER = sys.argv[3]
    iteration = sys.argv[4]

    print "==============================="
    print "Arrival Rate: ", arrivalRate
    print "Service Rate: ", serviceRate
    print "Max buffer size: ", MAXBUFFER
    print "Num of iteration: ", iteration
    print "==============================="

    if MAXBUFFER > 0:
        bufferQueue = Queue.Queue(MAXBUFFER) #finite size buffer
    else:
        bufferQueue = Queue.Queue() #infinite size buffer
    GEL = []
    
    #Create first event
    newEvent = CreateArrivalEvent()
    #Insert into list
    GEL.append(newEvent)
    #process arrival event

    for i in range(int(iteration)):
        #print GEL
        #print "queue size: ", bufferQueue.qsize()
        event = GEL.pop(0)
        if event.eventType == 'arrival':
            ProcessArrivalEvent(event)
        else:
            ProcessDepartureEvent(event)

    print "*******************************"
    #print "Mean Length: ", Stats.meanLength, " =>", 
    print "Mean Length: ", sum(Stats.meanLength)/float(len(Stats.meanLength))
    print "Busy time: ", Stats.busy, " /", time
    print "Packet dropped: ", Stats.dropped
    print "*******************************"

def negativeExpDistTime(rate):
    rand = random.random()
    return ((-1/float(rate))*math.log(1-rand))

def CreateArrivalEvent():
    global time, arrivalRate, serviceRate
    rand = negativeExpDistTime(arrivalRate) #this is for arrival
    rand2 = negativeExpDistTime(serviceRate) #this is service time
    eventtime = time + rand
    servicetime = rand2
    anEvent = Event(eventtime, 'arrival', servicetime) #new event
    return anEvent

def CreateDepartureEvent(servicetime):
    global time
    departuretime = time + servicetime
    anEvent = Event(departuretime, 'depart') #new event
    return anEvent

def ProcessArrivalEvent(event):
    print "ARRIVING: ", event.time
    
    global length, MAXBUFFER, bufferQueue, GEL, time, arrivalRate, serviceRate
    beforeTime = time
    time = event.time

    #generate next arrival event
    nextEvent = CreateArrivalEvent()
    GEL.append(nextEvent)
    sortGEL()
    
    #Process the arrival event
    qlength = bufferQueue.qsize() #update length with queue size
    servicetime = event.serviceTime
    if length == 0: #server is free, generate departure event
        departureEvent = CreateDepartureEvent(servicetime)
        GEL.append(departureEvent)
        sortGEL()
        length += 1 #increment # of packet
        #bufferQueue.put(event) #put packet in server queue
    else:
        if (qlength < int(MAXBUFFER)) or (int(MAXBUFFER) <= 0): #queue not full
            bufferQueue.put(event) #put in queue
            length += 1
            #print "buffer size: ", bufferQueue.qsize()
        else: #queue is full
            print "Dropping Packet"
            Stats.dropped = Stats.dropped + 1 #drop packet
        Stats.busy += (time - beforeTime)
    
    Stats.meanLength.append(bufferQueue.qsize()) #mean queue-length

def ProcessDepartureEvent(event):
    print "DEPARTING: ", event.time

    global time, bufferQueue, length
    beforeTime = time
    time = event.time #update time

    #update statistics
    Stats.meanLength.append(bufferQueue.qsize()) #mean queue-length
    Stats.busy += (time - beforeTime) #???????????

    length -= 1
    qlength = bufferQueue.qsize() #update length with q size
    if qlength == 0:
        #do nothing
        return
    else:
        #dequeue and create departure event
        arrivalEvent = bufferQueue.get()
        departureEvent = CreateDepartureEvent(arrivalEvent.serviceTime)
        GEL.append(departureEvent)
        sortGEL()

def sortGEL():
    global GEL
    GEL.sort(key=lambda e: e.time)
    
if __name__ == "__main__":
    main()

#fucntion do this
# do this
# do this
# do this
# do this
# do this
# return this
