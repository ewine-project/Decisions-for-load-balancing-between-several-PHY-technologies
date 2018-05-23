import socket
import queue
import threading
import time

RX_PORT1 = ("localhost", 50002)
RX_PORT2 = ("localhost", 50006)

txAddress = ("localhost", 60000)

ports = [RX_PORT1, RX_PORT2]

TIMEOUT = 0.1  # Number of seconds to wait for the correct packet before proceeding with the next best packet


def rxThread(sock, dataQueue, dataEvent, stopEvent):
    while not stopEvent.isSet():
        try:
            packet = sock.recv(2048)
            number = packet[0]*256 + packet[1]
            print ("RX packet", number)
            dataQueue.put((number, packet[2:]))
            dataEvent.set()
        except OSError:
            print ("Timeout on RX socket")
            pass
    print ("Stopping RX")


def txThread(sock, address, dataQueue, dataEvent, stopEvent):
    nextExpectedNumber = 0
    lastTransmission=time.time()
    while not stopEvent.isSet():
        dataEvent.wait(timeout=0.1)
        dataEvent.clear()
        try:
            while True:
                number, packet = dataQueue.get(timeout=0.1)
                if (number == nextExpectedNumber or
                    time.time() - lastTransmission > TIMEOUT):

                    nextExpectedNumber = number + 1
                    lastTransmission = time.time()
                    print ("Transmitting Number", number, " Buffered Packets:", dataQueue.qsize())
                    sock.sendto(packet, address)
                else:
                    dataQueue.put((number, packet))
                    break
        except queue.Empty:
            pass
    print ("Stopping TX")

def main():
    try:
        stopEvent = threading.Event()
        dataEvent = threading.Event()

        dataQueue = queue.PriorityQueue()

        threads = []

        for p in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(p)
            sock.settimeout(0.1)
            T = threading.Thread(target=rxThread, args=(sock, dataQueue, dataEvent, stopEvent))
            T.start()
            threads.append(T)

        txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        txSock.settimeout(0.1)
        T = threading.Thread(target=txThread, args=(txSock, txAddress, dataQueue, dataEvent, stopEvent))
        T.start()
        threads.append(T)

        while True:
            time.sleep(0.1)

    except Exception as E:
        print (E)
    finally:
        print ("Stopping...")
        stopEvent.set()
        [t.join() for t in threads]


if __name__ == '__main__':
    main()
