from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable

@dataclass
class ParameterInfo:
    name: str
    type: str
    default: Optional[Any]
    range: Optional[str]
    description: str

@dataclass
class ActionInfo:
    name: str
    method: Callable
    parameters: Dict[str, ParameterInfo]
    description: str

class Device(ABC):
    def __init__(self, name):
        self.name = name
        self.status = {'power': False}  # Common status attributes
        self._actions: Dict[str, ActionInfo] = {}

    def get_status(self):
        return {
            'name': self.name,
            'type': self.__class__.__name__,  # Add the device type
            'status': self.status
        }

    def set_status(self, **kwargs):
        self.status.update(kwargs)

    def get_actions(self):
        return self._actions

class SwitchableDevice(Device):
    def __init__(self, name):
        super().__init__(name)
        self._actions.update({
            'turn_on': ActionInfo(
                name='turn_on',
                method=self.turn_on,
                parameters={},
                description='Turn on the device.'
            ),
            'turn_off': ActionInfo(
                name='turn_off',
                method=self.turn_off,
                parameters={},
                description='Turn off the device.'
            ),
            'set_status': ActionInfo(
                name='set_status',
                method=self.set_status,
                parameters={},  # General method; parameters vary
                description='Set the status of the device.'
            ),
            'get_status': ActionInfo(
                name='get_status',
                method=self.get_status,
                parameters={},
                description='Get the status of the device.'
            ),
        })

    def turn_on(self):
        """Turn on the device."""
        self.set_status(power=True)

    def turn_off(self):
        """Turn off the device."""
        self.set_status(power=False)

# Simple Light, with brightness and color temperature
class Light(SwitchableDevice):
    def __init__(self, name, brightness=100, color_temp=2700):
        super().__init__(name)
        self.status['brightness'] = brightness  # Brightness level from 0 to 100
        self.status['color_temp'] = color_temp

        self._actions.update({
            'set_brightness': ActionInfo(
                name='set_brightness',
                method=self.set_brightness,
                parameters={
                    'brightness': ParameterInfo(
                        name='brightness',
                        type='int',
                        default=None,
                        range='0-100',
                        description='Brightness level between 0 and 100.'
                    )
                },
                description='Set the brightness of the light.'
            )
        })

        self._actions.update({
            'set_color_temp': ActionInfo(
                name='set_color_temp',
                method=self.set_color_temp,
                parameters={
                    'color_temp': ParameterInfo(
                        name='temperature',
                        type='int',
                        default=None,
                        range='2700-6500',
                        description='Color temperature in Kelvin'
                    )
                },
                description='Set the color temperature of the light'
            )
        })


    def set_brightness(self, brightness: int):
        """
        Set the brightness of the light.

        :param brightness: int - Brightness level between 0 and 100.
        """
        self.set_status(brightness=brightness)

    def set_color_temp(self, temp: int):
        """
        Set the color temperature of the light.

        :param temp: int - Color temperature in Kelvin.
        """
        self.set_status(color_temp=temp)

# Presence Sensor, check if there is a human present and update the status, along with the duration of presence
class PresenceSensor(Device):
    def __init__(self, name="Default Presence Sensor"):
        super().__init__(name)
        self.status.update({
            'human_present': False,
            'last_detection_time': None,
            'duration_of_presence': 0  # in minutes
        })

        self._actions.update({
            'update_presence': ActionInfo(
                name='update_presence',
                method=self.update_presence,
                parameters={
                    'detected': ParameterInfo(
                        name='detected',
                        type='bool',
                        default=None,
                        range='True or False',
                        description='Current presence status'
                    ),
                    'timestamp': ParameterInfo(
                        name='timestamp',
                        type='float',
                        default=None,
                        range='Unix timestamp',
                        description='Time of detection'
                    )
                },
                description='Update presence detection status'
            ),
            'get_presence_info': ActionInfo(
                name='get_presence_info',
                method=self.get_presence_info,
                parameters={},
                description='Get complete presence information'
            )
        })

    def update_presence(self, detected: bool, timestamp: float):
        previous_status = self.status['human_present']
        self.status['human_present'] = detected
        self.status['last_detection_time'] = timestamp
        
        if detected and previous_status:  # Still present
            # Update duration
            self.status['duration_of_presence'] = (timestamp - self.status['last_detection_time']) / 60
        elif detected and not previous_status:  # Just arrived
            self.status['duration_of_presence'] = 0

    def get_presence_info(self):
        return {
            'human_present': self.status['human_present'],
            'last_detection_time': self.status['last_detection_time'],
            'duration_of_presence': self.status['duration_of_presence']
        }   
# Air Conditioner, with temperature and mode
class AirConditioner(SwitchableDevice):
    def __init__(self, name, temperature=24, mode='cool'):
        super().__init__(name)
        self.status['temperature'] = temperature
        self.status['mode'] = mode

        self._actions.update({
            'set_temperature': ActionInfo(
                name='set_temperature',
                method=self.set_temperature,
                parameters={
                    'temperature': ParameterInfo(
                        name='temperature',
                        type='int',
                        default=None,
                        range='16-30',
                        description='Temperature between 16 and 30 degrees Celsius.'
                    )
                },
                description='Set the temperature of the air conditioner.'
            ),
            'set_mode': ActionInfo(
                name='set_mode',
                method=self.set_mode,
                parameters={
                    'mode': ParameterInfo(
                        name='mode',
                        type='str',
                        default='cool',
                        range='cool,heat,fan',
                        description='Operating mode of the AC'
                    )
                },
                description='Set the operating mode of the air conditioner.'
            )
        })

    def set_temperature(self, temperature: int):
        """Set the AC temperature"""
        self.set_status(temperature=temperature)

    def set_mode(self, mode: str):
        """Set the AC mode (cool/heat/fan)"""
        if mode in ['cool', 'heat', 'fan']:
            self.set_status(mode=mode)



# Smart Plug, with power consumption
class SmartPlug(SwitchableDevice):
    def __init__(self, name):
        super().__init__(name)
        self.status['power_consumption'] = 0.0

        self._actions.update({
            'get_power_consumption': ActionInfo(
                name='get_power_consumption',
                method=self.get_power_consumption,
                parameters={},
                description='Get current power consumption in watts.'
            ),
            'set_power_consumption': ActionInfo(
                name='set_power_consumption',
                method=self.set_power_consumption,
                parameters={
                    'watts': ParameterInfo(
                        name='watts',
                        type='float',
                        default=0.0,
                        range='0-3000',
                        description='Power consumption in watts'
                    )
                },
                description='Set current power consumption (for simulation)'
            )
        })

    def get_power_consumption(self):
        return self.status['power_consumption']

    def set_power_consumption(self, watts: float):
        self.set_status(power_consumption=watts)


