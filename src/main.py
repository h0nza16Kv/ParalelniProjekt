import time
from queue import Queue
from hotel import Hotel
from threads import Receptionist, RoomsMonitor, HostProducer

def main():
    hotel = Hotel(4)
    queue = Queue()

    producer = HostProducer(queue, interval=3)

    receptionists = [
        Receptionist(hotel, queue)
        for i in range(2)
    ]
    monitor = RoomsMonitor(hotel, interval=5)

    producer.start()
    for r in receptionists:
        r.start()
    monitor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

        producer.running = False
        for r in receptionists:
            r.running = False
        monitor.running = False

        for i in receptionists:
            queue.put(None)

        producer.join()
        for r in receptionists:
            r.join()
        monitor.join()

        print("Shutdown complete.")


if __name__ == "__main__":
    main()