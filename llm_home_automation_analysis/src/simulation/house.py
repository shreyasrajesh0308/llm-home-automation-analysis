class House:
    def __init__(self):
        self.rooms = {}

    def add_room(self, room):
        self.rooms[room.name] = room

    def get_room_status(self, room_name):
        if room_name in self.rooms:
            return self.rooms[room_name].get_status()
        raise ValueError(f"Room '{room_name}' not found")

    def set_room_status(self, room_name, device_name=None, human_status=None, **kwargs):
        if room_name in self.rooms:
            room = self.rooms[room_name]
            if device_name is not None:
                room.set_device_status(device_name, **kwargs)
            if human_status is not None:
                room.set_human_status(human_status)
        else:
            raise ValueError(f"Room '{room_name}' not found")

    def get_house_status(self):
        house_status = {'rooms': []}
        for room_name, room in self.rooms.items():
            room_status = room.get_status()
            house_status['rooms'].append(room_status)
        return house_status