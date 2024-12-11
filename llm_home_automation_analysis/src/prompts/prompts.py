from typing import Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass


EXAMPLES = {
    "simple": {
        "command": {
            "target_room_name": "Living Room",
            "device_name": "Living Room Light",
            "action": "turn_on",
            "parameters": None
        }
    },
    "with_parameters": {
        "command": {
            "target_room_name": "Bedroom",
            "device_name": "Bedroom AC",
            "action": "set_temperature",
            "parameters": {"temperature": 24}
        }
    },
    "composite": {
        "commands": [
            {
                "target_room_name": "Bedroom",
                "device_name": "Bedroom Light",
                "action": "turn_off",
                "parameters": {}
            },
            {
                "target_room_name": "Bedroom",
                "device_name": "Bedroom AC",
                "action": "set_mode",
                "parameters": {"mode": "cool"}
            }
        ]
    },
    "complex": {
        "commands": [
            {
                "target_room_name": "Bedroom",
                "device_name": "Bedroom Light",
                "action": "turn_off",
                "parameters": {}
            },
            {
                "target_room_name": "Bedroom",
                "device_name": "Bedroom AC",
                "action": "turn_off",
                "parameters": {}
            }
        ]
    }
}

# Function to build the prompt
def build_prompt(context: str, user_input: str) -> str:
    base_prompt = """
You are a natural language processing system for home automation. Your task is to convert user commands into structured actions that can control devices in different rooms. Each command should be converted into one or more specific device actions.

Available Rooms and Devices:
- Living Room: Light, AC
- Bedroom: Light, AC

Device Capabilities:
1. Lights:
   - turn_on/turn_off
   - set_brightness
    - Parameters: brightness (0-100)
   - set_color_temp
    - Parameters: color_temp (2700-6500K)
2. AC:
   - turn_on/turn_off
   - set_temperature
    - Parameters: temperature (16-30)
   - set_mode
    - Parameters: mode (cool/heat/fan)

Here are examples of how to process different types of commands:

1. Simple Command Example:
Input: "Turn on the living room light"
Output: {simple}

2. Command with Parameters Example:
Input: "Set bedroom AC temperature to 24 degrees"
Output: {with_parameters}

3. Composite Command Example:
Input: "Turn off bedroom light and set AC to cooling mode"
Output: {composite}

4. Complex Command Example:
Input: "If no one is in the bedroom, turn off all devices"
Output: {complex}

5. Invalid Command Examples (should return null):
- "Turn on bathroom light" (non-existent room)
- "Set kitchen AC temperature" (non-existent device)
- "Make it cooler" (too vague)
- "Set brightness to 150" (invalid parameter)

Your task is to parse the input command and return the appropriate structured output. For invalid commands, return null.

Context:
{context}

User Input:
{user_input}
"""
    # Format the prompt with all examples and inputs
    import json
    formatted_examples = {
        k: json.dumps(v, indent=4) for k, v in EXAMPLES.items()
    }
    return base_prompt.format(
        simple=formatted_examples["simple"],
        with_parameters=formatted_examples["with_parameters"],
        composite=formatted_examples["composite"],
        complex=formatted_examples["complex"],
        context=context,
        user_input=user_input
    )

@dataclass
class GPTAgentPrompt:
    system_prompt: str = """
    You are an AI assistant for home automation.
    """
    task_prompt: str = """
    {context}

    User Input:
    "{user_input}"

    Instructions:
    - Analyze the user input.
    - Determine the appropriate command to execute based on the available devices and actions.
    - You may need to make a decision based on the context of the user input.
    - You may need to run multiple commands to achieve the desired result.
    - Provide the result as a JSON object with the following fields:
    - target_room_name (string)
    - device_name (string)
    - action (string)
    - parameters (object, optional)

    Here are some examples of how you can use the commands:
    
    """

    task_prompt_examples: str = """

You are a natural language processing system for home automation. Your task is to convert user commands into structured actions that can control devices in different rooms. Each command should be converted into one or more specific device actions.

Available Rooms and Devices:
- Living Room: Light, AC
- Bedroom: Light, AC

Device Capabilities:
1. Lights:
   - turn_on/turn_off
   - set_brightness
    - Parameters: brightness (0-100)
   - set_color_temp
    - Parameters: color_temp (2700-6500K)
2. AC:
   - turn_on/turn_off
   - set_temperature
    - Parameters: temperature (16-30)
   - set_mode
    - Parameters: mode (cool/heat/fan)

Here are examples of how to process different types of commands:

1. Simple Command Example:
Input: "Turn on the living room light"
Output: {
    "command": {
        "target_room_name": "Living Room",
        "device_name": "Living Room Light",
        "action": "turn_on",
        "parameters": null
    }
}

2. Command with Parameters Example:
Input: "Set bedroom AC temperature to 24 degrees"
Output: {
    "command": {
        "target_room_name": "Bedroom",
        "device_name": "Bedroom AC",
        "action": "set_temperature",
        "parameters": {"temperature": 24}
    }
}

3. Composite Command Example:
Input: "Turn off bedroom light and set AC to cooling mode"
Output: {
    "commands": [
        {
            "target_room_name": "Bedroom",
            "device_name": "Bedroom Light",
            "action": "turn_off",
            "parameters": {}
        },
        {
            "target_room_name": "Bedroom",
            "device_name": "Bedroom AC",
            "action": "set_mode",
            "parameters": {"mode": "cool"}
        }
    ]
}

4. Complex Command Example:
Input: "If no one is in the bedroom, turn off all devices"
Output: {
    "commands": [
        {
            "target_room_name": "Bedroom",
            "device_name": "Bedroom Light",
            "action": "turn_off",
            "parameters": {}
        },
        {
            "target_room_name": "Bedroom",
            "device_name": "Bedroom AC",
            "action": "turn_off",
            "parameters": {}
        }
    ]
}

5. Invalid Command Examples (should return null):
- "Turn on bathroom light" (non-existent room)
- "Set kitchen AC temperature" (non-existent device)
- "Make it cooler" (too vague)
- "Set brightness to 150" (invalid parameter)

Your task is to parse the input command and return the appropriate structured output. For invalid commands, return null.

Context:
"{context}"

User Input:
"{user_input}"

    """
# Experiment to see if the reasoning is useful
class CommandsOutputsWithReasoning(BaseModel):
    class CommandOutput(BaseModel):
        target_room_name: str = Field(..., description="The name of the room where the device is located.")
        device_name: str = Field(..., description="The name of the device to control.")
        action: str = Field(..., description="The action to perform on the device.")
        parameters: Optional[str] = Field(default=None, description="Additional parameters for the action. Has to be a string that can be parsed into a dictionary.")

    commands: list[CommandOutput] = Field(..., description="The list of commands to execute.")
    reasoning: str = Field(..., description="Provide a detailed reasoning for the commands that have to be run")

class CommandsOutputs(BaseModel):
    class CommandOutput(BaseModel):
        target_room_name: str = Field(..., description="The name of the room where the device is located.")
        device_name: str = Field(..., description="The name of the device to control.")
        action: str = Field(..., description="The action to perform on the device.")
        parameters: Optional[dict] = Field(default=None, description="Additional parameters for the action.")

    commands: list[CommandOutput] = Field(..., description="The list of commands to execute.")
