class House:
    def __init__(self):
        self.rooms = []

    def add_room(self, room):
        self.rooms.append(room)

    def get_room_status(self, room_name):
        for room in self.rooms:
            if room.name == room_name:
                status = {
                    'room_name': room.name,
                    'devices': [device.get_status() for device in room.devices],
                    'human_status': room.get_human_status()
                }
                return status
        raise ValueError(f"Room '{room_name}' not found")

    def set_room_status(self, room_name, device_name=None, device_status=None, human_status=None):
        for room in self.rooms:
            if room.name == room_name:
                if device_name is not None and device_status is not None:
                    room.set_device_status(device_name, device_status)
                if human_status is not None:
                    room.set_human_status(human_status)
                return
        raise ValueError(f"Room '{room_name}' not found")