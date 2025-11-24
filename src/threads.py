import threading
import time
from host import Host
import random
from queue import Empty

class HostProducer(threading.Thread):
    def __init__(self, host_queue, start_id=1, interval=5):
        super().__init__()
        self.host_queue = host_queue
        self.host_id = start_id
        self.interval = interval
        self.running = True

    def run(self):
        """
        It triggers an infinite cycle of generating new guests.
        The method runs as long as the `self.running` attribute is set to True.
        In each iteration, it creates a new guest with a unique ID and a randomly generated length of stay.
        The guest is added to the `host_queue` queue, where it waits to be served.
        :return: None
        """
        while self.running:
            new_host = Host(self.host_id, stay_time=random.randint(5, 10))

            self.host_queue.put(new_host)
            print(f"\nThe guest {self.host_id} came and waiting in queue")

            self.host_id += 1

            time.sleep(self.interval)


class Receptionist(threading.Thread):
    def __init__(self, hotel, host_queue):
        super().__init__()
        self.hotel = hotel
        self.host_queue = host_queue
        self.running = True

    def run(self):
        """
         Serves guests arriving at the queue and arranges their accommodation.
         If the guest is successfully acquired:
            -  if the guest is `None`, this is a signal to terminate and the thread is terminated,
            - if there is a vacant room in the hotel, the guest is accommodated and a new thread is started
                to simulate their stay (`stay_and_checkout`),
            - if the hotel has no free rooms, the guest is refused and leaves.

        After processing each guest, `task_done()` is called so that it is correctly
        marked as completed in the queue.
        :return: None
        """
        while self.running:
            host = None
            try:
                host = self.host_queue.get(timeout=0.1)
            except Empty:
                continue

            if host is None:
                self.host_queue.task_done()
                break

            room_number = self.hotel.reserve_room(host)
            if room_number:
                host.check_in(room_number)
                threading.Thread(target=self.stay_and_checkout, args=(host, self.hotel)).start()
            else:
                print(f"\nThe guest {host.host_id} leaving, hotel is full.")

            self.host_queue.task_done()

    @staticmethod
    def stay_and_checkout(host, hotel):
        """
         The method first puts the thread to sleep for a period corresponding to the length of the guest's stay
        (`host.stay_time`). After this period has elapsed, it releases the hotel room and
        then calls the guest's `check_out()` method, whereby the guest officially leaves the hotel.
        :param host: the property of the guest who is currently staying there
        :param hotel: the hotel building in which the guest is staying
        :return: None
        """
        time.sleep(host.stay_time)
        room_to_release = host.assigned_room
        host.check_out()
        hotel.release_room(room_to_release)


class RoomsMonitor(threading.Thread):
    def __init__(self, hotel, interval=5):
        super().__init__()
        self.hotel = hotel
        self.interval = interval
        self.running = True

    def run(self):
        """
        Regularly monitors the availability of rooms in the hotel.
        :return: None
        """
        while self.running:
            with self.hotel.lock:
                free = len(self.hotel.free_rooms)

            print(f"\nAvailable rooms : {free}")
            time.sleep(self.interval)