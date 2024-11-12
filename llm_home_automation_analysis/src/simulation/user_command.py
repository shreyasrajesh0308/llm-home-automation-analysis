from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner

class User_Command:
    def __init__(self, source_room, target_room, action, parameters=None):
        self.source_room = source_room      # Room object
        self.target_room = target_room      # Room object
        self.action = action.lower()        # Normalize action string
        self.parameters = parameters or {}  # Dictionary of parameters

    def execute(self):
        if self.action == "turn on light":
            self._turn_on_light()
        elif self.action == "turn off light":
            self._turn_off_light()
        elif self.action == "turn on air conditioner":
            self._turn_on_air_conditioner()
        elif self.action == "turn off air conditioner":
            self._turn_off_air_conditioner()
        elif self.action == "set temperature":
            self._set_temperature()
        elif self.action == "report status":
            return self._report_status()
        elif self.action == "set brightness":
            self._set_brightness()
        else:
            raise ValueError(f"Unknown action '{self.action}'")

    def _turn_on_light(self):
        # Find the light device in the target room and turn it on
        for device in self.target_room.devices:
            if isinstance(device, Light):
                device.set_status(True)
                print(f"Light in {self.target_room.name} turned on.")
                return
        print(f"No light found in {self.target_room.name}.")

    def _turn_off_light(self):
        # Find the light device in the target room and turn it off
        for device in self.target_room.devices:
            if isinstance(device, Light):
                device.set_status(False)
                print(f"Light in {self.target_room.name} turned off.")
                return
        print(f"No light found in {self.target_room.name}.")
        
    def _set_brightness(self):
        for device in self.target_room.devices:
            if isinstance(device, Light):
                brightness = self.parameters.get('brightness')
                if brightness is None:
                    print("Brightness value not provided.")
                    return
                device.set_brightness(brightness)
                print(f"Light in {self.target_room.name} set to brightness {brightness}.")
                return
        print(f"No light found in {self.target_room.name}.")
        return
    def _turn_on_air_conditioner(self):
        # Find the air conditioner device in the target room and turn it on
        for device in self.target_room.devices:
            if isinstance(device, AirConditioner):
                device.set_status(True)
                print(f"Air conditioner in {self.target_room.name} turned on.")
                return
        print(f"No air conditioner found in {self.target_room.name}.")
    def _turn_off_air_conditioner(self):
        # Find the air conditioner device in the target room and turn it off
        for device in self.target_room.devices:
            if isinstance(device, AirConditioner):
                device.set_status(False)
                print(f"Air conditioner in {self.target_room.name} turned off.")
                return
        print(f"No air conditioner found in {self.target_room.name}.")
    def _set_temperature(self):
        # Set the temperature of the air conditioner in the target room
        temp = self.parameters.get('temperature')
        if temp is None:
            print("Temperature value not provided.")
            return
        for device in self.target_room.devices:
            if isinstance(device, AirConditioner):
                device.set_status(True)
                device.set_temperature(temp)
                print(f"Air conditioner in {self.target_room.name} set to {temp}°C.")
                return
        print(f"No air conditioner found in {self.target_room.name}.")

    def _report_status(self):
        # Return the status of the target room
        status = self.target_room.get_status()
        print(f"Status of {self.target_room.name}: {status}")
        return status
if __name__ == "__main__":
    print("This is an instruction module for home automation simulation.")
