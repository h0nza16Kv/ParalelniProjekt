class Host:
    def __init__(self, host_id, stay_time):
        self.host_id = host_id
        self.stay_time = stay_time
        self.assigned_room = None
        self.status = "waiting"

    def check_in(self, room_number):
        """
        Accommodates the guest in the specified room.
        The method sets the guest's room number, updates their status to
        "accommodated"
        :param room_number: room number where the guest is staying
        :return: None
        """
        self.assigned_room = room_number
        self.status = "accommodated"
        print(f"The guest {self.host_id} stayed in a room {room_number}.")

    def check_out(self):
        """
        Checks out the guest from their current room.
        The method prints a message about the guest's departure, deletes the information about the assigned
        room, and updates the guest's status to "left."
        :return: None
        """
        print(f"The guest {self.host_id} is leaving a room {self.assigned_room}.")
        self.assigned_room = None
        self.status = "left"