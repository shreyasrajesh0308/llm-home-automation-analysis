from llm_home_automation_analysis.src.device import Device, HumanStatusReporter
class Room:
    def __init__(self, name):
        self.name = name
        self.devices = []
        self.human_status_reporter = HumanStatusReporter()

    def add_device(self, device):
        self.devices.append(device)

    def get_device_status(self, device_name):
        for device in self.devices:
            if device.name == device_name:
                return device.get_status()
        raise ValueError(f"Device '{device_name}' not found in room '{self.name}'")

    def set_device_status(self, device_name, status):
        for device in self.devices:
            if device.name == device_name:
                device.set_status(status)
                return
        raise ValueError(f"Device '{device_name}' not found in room '{self.name}'")

    def get_human_status(self):
        return self.human_status_reporter.get_status()

    def set_human_status(self, is_present):
        self.human_status_reporter.set_status(is_present)