import unittest
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from src.hotel import Hotel
from src.host import Host
from src.threads import Receptionist
from unittest.mock import patch


class TestHotelSystem(unittest.TestCase):

    def setUp(self):
        self.executor = ThreadPoolExecutor(max_workers=1)

    def tearDown(self):
        self.executor.shutdown(wait=False)

    def test_hotel_initialization(self):
        """Test initial state of the Hotel (using rooms dictionary)."""
        hotel = Hotel(num_rooms=3)
        self.assertEqual(hotel.num_rooms, 3)
        self.assertEqual(len(hotel.rooms), 3)
        # Ověří, že všechny pokoje mají stav 'free'
        self.assertTrue(all(status == 'free' for status in hotel.rooms.values()))

    def test_reserve_and_release_room(self):
        """Test basic reserve and release operations (checking room states)."""
        hotel = Hotel(num_rooms=1)
        host1 = Host(1, 5)

        # Rezervace
        room1 = hotel.reserve_room(host1)
        self.assertEqual(room1, 1)
        self.assertEqual(hotel.rooms[1], 'occupied')

        room2 = hotel.reserve_room(host1)
        self.assertIsNone(room2)

        hotel.release_room(room1)
        self.assertEqual(hotel.rooms[1], 'cleaning')

        room3 = hotel.reserve_room(host1)
        self.assertIsNone(room3)

    def test_release_room_safety(self):
        """
        Test that releasing a room correctly sets the state to 'cleaning'.
        (Původní test kontroloval integritu seznamu free_rooms, zde kontrolujeme stav).
        """
        hotel = Hotel(num_rooms=2)


        room_reserved = hotel.reserve_room(Host(1, 1))  # např. 1
        self.assertEqual(hotel.rooms[room_reserved], 'occupied')

        hotel.release_room(room_reserved)
        self.assertEqual(hotel.rooms[room_reserved], 'cleaning')

        hotel.release_room(room_reserved)
        self.assertEqual(hotel.rooms[room_reserved], 'cleaning')

    def test_thread_safe_reservation(self):
        """Test thread-safe room reservation under contention (using rooms dictionary)."""
        NUM_ROOMS = 5
        NUM_THREADS = 10
        hotel = Hotel(NUM_ROOMS)
        reserved_rooms = []

        def worker():
            host = Host(threading.get_ident(), 1)
            room = hotel.reserve_room(host)
            if room is not None:
                reserved_rooms.append(room)

        threads = []
        for _ in range(NUM_THREADS):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(reserved_rooms), NUM_ROOMS)
        self.assertEqual(len(set(reserved_rooms)), NUM_ROOMS)
        for room in reserved_rooms:
            self.assertTrue(1 <= room <= NUM_ROOMS)
            self.assertEqual(hotel.rooms[room], 'occupied')

    def test_receptionist_check_in_full_hotel(self):
        """
        Test Receptionist behavior when the hotel is full and correctly refuses the next host.
        """
        hotel = Hotel(num_rooms=1)
        host_queue = Queue()
        receptionist = Receptionist(hotel, host_queue, self.executor)

        host1 = Host(1, 10)
        host_queue.put(host1)

        with patch.object(receptionist, 'stay_and_checkout'):
            host_queue.put(None)
            receptionist.run()

            self.assertEqual(hotel.rooms[1], 'occupied')

            host_queue = Queue()
            receptionist.host_queue = host_queue

            host2 = Host(2, 5)
            host_queue.put(host2)
            host_queue.put(None)

            receptionist.run()

        self.assertEqual(hotel.rooms[1], 'occupied')
        self.assertEqual(host2.status, "waiting")
        self.assertIsNone(host2.assigned_room)


if __name__ == '__main__':
    unittest.main()