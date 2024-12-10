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

class Light(SwitchableDevice):
    def __init__(self, name, brightness=100):
        super().__init__(name)
        self.status['brightness'] = brightness  # Brightness level from 0 to 100

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

    def set_brightness(self, brightness: int):
        """
        Set the brightness of the light.

        :param brightness: int - Brightness level between 0 and 100.
        """
        self.set_status(brightness=brightness)

class AirConditioner(SwitchableDevice):
    def __init__(self, name, temperature=24):
        super().__init__(name)
        self.status['temperature'] = temperature  # Temperature in Celsius

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
            )
        })

    def set_temperature(self, temperature: int):
        """
        Set the air conditioner's temperature.

        :param temperature: int - Desired temperature between 16 and 30 degrees Celsius.
        """
        self.set_status(temperature=temperature)

class HumanStatusReporter(Device):
    def __init__(self):
        super().__init__(name="HumanStatusReporter")
        self.status['human_present'] = False

        self._actions.update({
            'set_status': ActionInfo(
                name='set_status',
                method=self.set_status,
                parameters={
                    'human_present': ParameterInfo(
                        name='human_present',
                        type='bool',
                        default=None,
                        range='True or False',
                        description='Set whether a human is present.'
                    )
                },
                description='Set the human presence status.'
            ),
            'get_status': ActionInfo(
                name='get_status',
                method=self.get_status,
                parameters={},
                description='Get the human presence status.'
            ),
        })

    def set_status(self, **kwargs):
        if 'human_present' in kwargs:
            self.status['human_present'] = kwargs['human_present']
        super().set_status(**kwargs)
