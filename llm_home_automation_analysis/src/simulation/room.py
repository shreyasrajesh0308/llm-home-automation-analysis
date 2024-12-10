from llm_home_automation_analysis.src.simulation.device import Device, HumanStatusReporter

class Room:
    def __init__(self, name):
        self.name = name
        self.devices = {}
        self.human_status_reporter = HumanStatusReporter()

    def add_device(self, device: Device):
        self.devices[device.name] = device

    def get_device_status(self, device_name):
        if device_name in self.devices:
            return self.devices[device_name].get_status()
        raise ValueError(f"Device '{device_name}' not found in room '{self.name}'")

    def set_device_status(self, device_name, **kwargs):
        if device_name in self.devices:
            self.devices[device_name].set_status(**kwargs)
        else:
            raise ValueError(f"Device '{device_name}' not found in room '{self.name}'")

    def get_human_status(self):
        return self.human_status_reporter.get_status()

    def set_human_status(self, is_present):
        self.human_status_reporter.set_status(human_present=is_present)

    def get_status(self):
        return {
            'room_name': self.name,
            'devices': {
                device_name: device.get_status() for device_name, device in self.devices.items()
            },
            'human_status': self.human_status_reporter.get_status()
        }