import inspect
from llm_home_automation_analysis.src.simulation.device import Device
from llm_home_automation_analysis.src.simulation.house import House

class UserCommand:
    def __init__(self, house):
        self.house = house

    def execute(self, target_room_name, device_name, action, parameters=None):
        target_room = self.house.rooms.get(target_room_name)
        if not target_room:
            raise ValueError(f"Room '{target_room_name}' not found.")
        device = target_room.devices.get(device_name)
        if not device:
            raise ValueError(f"Device '{device_name}' not found in room '{target_room_name}'.")

        actions = device.get_actions()
        if action in actions:
            action_info = actions[action]
            method = action_info.method
            if parameters:
                method(**parameters)
            else:
                method()
            print(f"Executed action '{action}' on device '{device_name}' in room '{target_room_name}'.")
        else:
            raise ValueError(f"Action '{action}' is not supported by device '{device_name}'.")

    def list_devices(self, room_name):
        room = self.house.rooms.get(room_name)
        if not room:
            raise ValueError(f"Room '{room_name}' not found.")
        return list(room.devices.keys())

    def list_device_actions(self, room_name, device_name):
        room = self.house.rooms.get(room_name)
        if not room:
            raise ValueError(f"Room '{room_name}' not found.")
        device = room.devices.get(device_name)
        if not device:
            raise ValueError(f"Device '{device_name}' not found in room '{room_name}'.")
        actions = device.get_actions()
        return {action_name: {
            'description': action_info.description,
            'parameters': {
                param_name: {
                    'type': param_info.type,
                    'range': param_info.range,
                    'description': param_info.description
                } for param_name, param_info in action_info.parameters.items()
            }
        } for action_name, action_info in actions.items()}

    def get_action_parameters(self, room_name, device_name, action):
        room = self.house.rooms.get(room_name)
        if not room:
            raise ValueError(f"Room '{room_name}' not found.")
        device = room.devices.get(device_name)
        if not device:
            raise ValueError(f"Device '{device_name}' not found in room '{room_name}'.")

        actions = device.get_actions()
        if action in actions:
            action_info = actions[action]
            parameters = {
                param_name: {
                    'type': param_info.type,
                    'range': param_info.range,
                    'description': param_info.description
                } for param_name, param_info in action_info.parameters.items()
            }
            return {
                'description': action_info.description,
                'parameters': parameters
            }
        else:
            raise ValueError(f"Action '{action}' is not supported by device '{device_name}'.")

    def get_house_structure(self):
        structure = {}
        for room_name, room in self.house.rooms.items():
            structure[room_name] = list(room.devices.keys())
        return structure
    def execute_room_action(self, target_room_name, action, parameters=None):
        room = self.house.rooms.get(target_room_name)
        if not room:
            raise ValueError(f"Room '{target_room_name}' not found.")

        for device_name, device in room.devices.items():
            if action in device.get_actions():
                method = getattr(device, action)
                if parameters:
                    method(**parameters)
                else:
                    method()
                print(f"Executed action '{action}' on device '{device_name}' in room '{target_room_name}'.")
            else:
                print(f"Action '{action}' is not supported by device '{device_name}'.")

    def get_room_status(self, room_name):
        return self.house.get_room_status(room_name)