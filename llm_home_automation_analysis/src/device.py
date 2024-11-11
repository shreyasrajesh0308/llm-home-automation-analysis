class Device:
    def __init__(self, name):
        self.name = name
        self.status = False  # False = Off, True = On

    def get_status(self):
        return {'name': self.name, 'status': self.status}

    def set_status(self, status):
        self.status = status


class Light(Device):
    def __init__(self, name, brightness=100):
        super().__init__(name)
        self.brightness = brightness  # Brightness level from 0 to 100

    def get_status(self):
        status = super().get_status()
        status['brightness'] = self.brightness
        return status

    def set_brightness(self, brightness):
        if 0 <= brightness <= 100:
            self.brightness = brightness
        else:
            raise ValueError("Brightness must be between 0 and 100")


class AirConditioner(Device):
    def __init__(self, name, temperature=24):
        super().__init__(name)
        self.temperature = temperature  # Temperature in Celsius

    def get_status(self):
        status = super().get_status()
        status['temperature'] = self.temperature
        return status

    def set_temperature(self, temperature):
        if 16 <= temperature <= 30:
            self.temperature = temperature
        else:
            raise ValueError("Temperature must be between 16 and 30 Celsius")


class HumanStatusReporter:
    def __init__(self):
        self.is_present = False

    def get_status(self):
        return {'human_present': self.is_present}

    def set_status(self, is_present):
        self.is_present = is_present
