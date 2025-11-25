import threading


class Hotel:
    def __init__(self, num_rooms):
        self.num_rooms = num_rooms
        self.rooms = {i: 'free' for i in range(1, num_rooms + 1)}
        self.lock = threading.Lock()
        self.free_rooms_cond = threading.Condition(self.lock)

    def reserve_room(self, host):
        """
        Reserves the first available room for the guest.
        :param host: guest information
        :return: Reserved room number, or None if no rooms are available
        """
        with self.lock:
            free_rooms = [r for r, status in self.rooms.items() if status == 'free']

            if free_rooms:
                room_number = free_rooms[0]
                self.rooms[room_number] = 'occupied'
                return room_number
            else:
                return None

    def release_room(self, room_number):
        """
         Releases the room and adds it back to the list of available rooms.
        :param room_number: number of room
        :return: None
        """
        with self.lock:
            self.rooms[room_number] = 'cleaning'
            print(f"Room {room_number} is now scheduled for cleaning.")

    def finish_cleaning(self, room_number):
        """
        Sets the room to 'free' status after cleaning is complete
        :param room_number: room number
        :return: None
        """
        with self.lock:
            self.rooms[room_number] = 'free'
            print(f"Room {room_number} is clean and ready.")
            self.free_rooms_cond.notify_all()