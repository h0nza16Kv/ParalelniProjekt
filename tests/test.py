import unittest
import threading
from queue import Queue

from src.hotel import Hotel
from src.host import Host
from src.threads import Receptionist


class TestHotelSystem(unittest.TestCase):

    def test_hotel_initialization(self):
        """Test initial state of the Hotel."""
        hotel = Hotel(num_rooms=3)
        self.assertEqual(hotel.num_rooms, 3)
        self.assertEqual(len(hotel.free_rooms), 3)
        self.assertListEqual(hotel.free_rooms, [1, 2, 3])

    def test_reserve_and_release_room(self):
        """Test basic reserve and release operations."""
        hotel = Hotel(num_rooms=1)
        host1 = Host(1, 5)

        room1 = hotel.reserve_room(host1)
        self.assertEqual(room1, 1)
        self.assertEqual(len(hotel.free_rooms), 0)

        room2 = hotel.reserve_room(host1)
        self.assertIsNone(room2)

        hotel.release_room(room1)
        self.assertEqual(len(hotel.free_rooms), 1)
        self.assertIn(1, hotel.free_rooms)

    def test_release_room_safety(self):
        """
        Test that release_room prevents adding a room that is already in free_rooms.
        This tests the integrity of the free_rooms list.
        """
        hotel = Hotel(num_rooms=2)

        self.assertEqual(len(hotel.free_rooms), 2)

        room_reserved = hotel.reserve_room(Host(1, 1))
        self.assertEqual(len(hotel.free_rooms), 1)

        hotel.release_room(room_reserved)
        self.assertEqual(len(hotel.free_rooms), 2)
        self.assertIn(room_reserved, hotel.free_rooms)

        hotel.release_room(room_reserved)

        self.assertEqual(len(hotel.free_rooms), 2)
        self.assertEqual(len(set(hotel.free_rooms)), 2)


    def test_thread_safe_reservation(self):
        """Test thread-safe room reservation under contention."""
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

    def test_receptionist_check_in_full_hotel(self):
        """
        Test Receptionist behavior when the hotel is full and correctly refuses the next host.
        """
        hotel = Hotel(num_rooms=1)
        host_queue = Queue()
        receptionist = Receptionist(hotel, host_queue)

        host1 = Host(1, 10)
        host_queue.put(host1)
        host_queue.put(None)

        receptionist.run()
        self.assertEqual(len(hotel.free_rooms), 0)

        host2 = Host(2, 5)
        host_queue.put(host2)
        host_queue.put(None)

        receptionist.run()

        self.assertEqual(len(hotel.free_rooms), 0)
        self.assertEqual(host2.status, "waiting")


if __name__ == '__main__':
    unittest.main()