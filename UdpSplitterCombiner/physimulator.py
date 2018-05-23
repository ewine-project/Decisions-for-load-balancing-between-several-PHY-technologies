import socket
import time
import threading
import sys

import random

RX_PORT1 = ("localhost", 50001)
RX_PORT2 = ("localhost", 50005)
rx_ports = [RX_PORT1, RX_PORT2]

TX_PORT1 = ("localhost", 50002)
TX_PORT2 = ("localhost", 50006)
tx_ports = [TX_PORT1, TX_PORT2]

MISS_PROB = 0.01  # probability that a packet is lost on the PHY
DELAY_PROB = 0.05  # probability to delay a packet, to create some artificial order mixing of the pachets


def forwardThread(rxSock, txSock, txAddress, stopEvent):
    while not stopEvent.isSet():
        try:
            data = rxSock.recv(2048)
            if (random.random() <= MISS_PROB):
                sys.stdout.write('m')
                continue
            if (random.random() <= DELAY_PROB):
                time.sleep(random.random() * 0.2) # wait up to 200 ms
                sys.stdout.write('d')
            else:
                sys.stdout.write('.')
            txSock.sendto(data, txAddress)
        except OSError:
            sys.stdout.write('t')
        finally:
            sys.stdout.flush()
            pass
        pass

def main():
    threads = []
    stopEvent = threading.Event()

    try:
        for (rxAddress, txAddress) in zip(rx_ports, tx_ports):
            print ("Setting up", rxAddress, " to ", txAddress)
            rxSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            rxSock.settimeout(0.1)
            rxSock.bind(rxAddress)

            txSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            txSock.settimeout(0.1)

            T = threading.Thread(target=forwardThread, args=(rxSock, txSock, txAddress, stopEvent))
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
