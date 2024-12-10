import json
import os
from pydantic import BaseModel, Field
import openai

from llm_home_automation_analysis.src.simulation.house import House
from llm_home_automation_analysis.src.simulation.room import Room
from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner
from llm_home_automation_analysis.src.simulation.user_command import UserCommand

# Set your OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is set as an environment variable
#set env variable

def setup_simulation():
    # Create devices
    light1 = Light(name="Living Room Light")
    ac1 = AirConditioner(name="Living Room AC")
    light2 = Light(name="Bedroom Light")
    ac2 = AirConditioner(name="Bedroom AC")

    # Create rooms and add devices
    living_room = Room(name="Living Room")
    living_room.add_device(light1)
    living_room.add_device(ac1)
    living_room.set_human_status(True)

    bedroom = Room(name="Bedroom")
    bedroom.add_device(light2)
    bedroom.add_device(ac2)
    bedroom.set_human_status(False)

    # Create house and add rooms
    my_house = House()
    my_house.add_room(living_room)
    my_house.add_room(bedroom)

    # Create UserCommand instance
    command_interface = UserCommand(my_house)

    return my_house, command_interface

def generate_commands(house):
    """Generates commands dynamically based on the house configuration."""
    commands = []
    for room_name, room in house.rooms.items():
        for device_name, device in room.devices.items():
            actions = device.get_actions()
            for action_name, action_info in actions.items():
                parameters = {}
                if action_info.parameters:
                    # For each parameter, generate possible values
                    for param_name, param_info in action_info.parameters.items():
                        # Depending on the parameter type, create some example values
                        if param_info.type == 'int':
                            # Assume some example integer values within the range if specified
                            if param_info.range:
                                min_val, max_val = map(int, param_info.range.split('-'))
                                example_values = [min_val, (min_val + max_val) // 2, max_val]
                            else:
                                example_values = [0, 50, 100]
                            for value in example_values:
                                parameters[param_name] = value
                                command = {
                                    'target_room_name': room_name,
                                    'device_name': device_name,
                                    'action': action_name,
                                    'parameters': parameters.copy()
                                }
                                commands.append(command)
                        elif param_info.type == 'bool':
                            for value in [True, False]:
                                parameters[param_name] = value
                                command = {
                                    'target_room_name': room_name,
                                    'device_name': device_name,
                                    'action': action_name,
                                    'parameters': parameters.copy()
                                }
                                commands.append(command)
                        else:
                            # For other types, define example values as needed
                            pass
                else:
                    # If no parameters, add the command directly
                    command = {
                        'target_room_name': room_name,
                        'device_name': device_name,
                        'action': action_name,
                        'parameters': parameters.copy()
                    }
                    commands.append(command)
    return commands

def convert_command_to_natural_language(command):
    """Converts a command dictionary to natural language instructions using OpenAI's API."""
    # Construct the system prompt with updated examples matching the new command set
    system_prompt = {
        "role": "system",
        "content": (
            "You are an assistant that converts structured home automation commands into natural language instructions. "
            "Each command includes the following fields:\n"
            "- 'target_room_name': The room where the action should be performed.\n"
            "- 'device_name': The name of the device to control.\n"
            "- 'action': The action to perform on the device (e.g., 'turn_on', 'turn_off', 'set_temperature', 'set_brightness').\n"
            "- 'parameters': Additional parameters required for the action (e.g., {'temperature': 22}).\n\n"
            "Your task is to generate a list of polite, natural-sounding commands that a user might say to perform the 'action' on the 'device_name' in the 'target_room_name'. "
            "Include both direct requests and indirect expressions (e.g., expressions of feeling). "
            "Ensure each command is concise and uses appropriate language for the given action and parameters.\n\n"
            "For example, if the command is:\n"
            "{\n"
            '  "target_room_name": "Living Room",\n'
            '  "device_name": "Living Room AC",\n'
            '  "action": "set_temperature",\n'
            '  "parameters": {"temperature": 22}\n'
            "}\n"
            "You might generate:\n"
            '- "Please set the living room AC to 22 degrees."\n'
            '- "It is a bit warm in the living room; could you lower the temperature?"\n'
            '- "I would like the living room to be cooler."\n\n'
            "Use similar phrasing and adjust pronouns like 'here' or 'in the [room name]' based on whether the speaker is likely in the 'target_room_name'."
        )
    }

    task_prompt = f"Convert the following command to natural language instructions:\n\nCommand:\n{json.dumps(command, indent=2)}"

    messages = [
        system_prompt,
        {"role": "user", "content": task_prompt}
    ]

    class NaturalLanguageOutput(BaseModel):
        instructions: list[str] = Field(..., description="A list of natural language commands.")

    client = openai.OpenAI()
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        response_format=NaturalLanguageOutput,
    )

    return response.choices[0].message.parsed  # Returns a list of instructions

def main():
    # Setup simulation
    my_house, command_interface = setup_simulation()

    # Save the initial house state
    house_state = my_house.get_house_status()

    # Make dir if not exists
    os.makedirs('asset', exist_ok=True)

    # Save the initial house state
    with open('asset/house_state.json', 'w') as f:
        json.dump(house_state, f, indent=2)
        print("Initial house state saved to 'house_state.json'.")

    # Generate commands dynamically
    commands = generate_commands(my_house)

    # Save the commands to a JSON file
    with open('asset/commands.json', 'w') as f:
        json.dump(commands, f, indent=2)
        print(f"{len(commands)} commands saved to 'commands.json'.")

    # Convert commands to natural language and save them
    nl_commands = []
    for idx, command in enumerate(commands):
        nl_instructions = convert_command_to_natural_language(command)
        for instruction in nl_instructions:
            nl_commands.append({
                'command': command,
                'natural_language': instruction
            })
        print(f"Converting to natural language: {idx+1}/{len(commands)}.")

    # Save the natural language commands
    with open('asset/nl_commands.json', 'w') as f:
        json.dump(nl_commands, f, indent=2)
        print(f"{len(nl_commands)} natural language commands saved to 'nl_commands.json'.")

if __name__ == "__main__":
    main()
