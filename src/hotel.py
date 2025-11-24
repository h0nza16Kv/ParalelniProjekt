import threading

class Hotel:
    def __init__(self, num_rooms):
        self.num_rooms = num_rooms
        self.free_rooms = list(range(1, num_rooms + 1))
        self.lock = threading.Lock()

    def reserve_room(self, host):
        """
        Reserves the first available room for the guest.
        :param host: guest information
        :return: None
        """
        with self.lock:
            if self.free_rooms:
                room_number = self.free_rooms.pop(0)
                return room_number
            else:
                return None

    def release_room(self, room_number):
        """
        Releases the specified room and adds it back to the list of available rooms.
        :param room_number: room number to be made available
        :return:None
        """
        with self.lock:
            if room_number not in self.free_rooms:
                self.free_rooms.append(room_number)