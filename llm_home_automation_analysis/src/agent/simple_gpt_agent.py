import json
import os
from pydantic import BaseModel, Field
import openai
from typing import Optional
from collections import defaultdict

from llm_home_automation_analysis.src.simulation.house import House
from llm_home_automation_analysis.src.simulation.room import Room
from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner
from llm_home_automation_analysis.src.simulation.user_command import UserCommand


class CommandArguments(BaseModel):
    target_room_name: str = Field(..., description="The name of the room where the device is located.")
    device_name: str = Field(..., description="The name of the device to control.")
    action: str = Field(..., description="The action to perform on the device.")
    parameters: dict = Field(default_factory=dict, description="Additional parameters required for the action.")

class GPTAgent:
    def __init__(self, house, command_interface):
        self.house = house
        self.command_interface = command_interface

    def build_context(self):
        # Build context with house structure and available actions
        house_structure = self.command_interface.get_house_structure()
        context = "House Structure and Available Actions:\n"
        for room_name, devices in house_structure.items():
            context += f"- {room_name}:\n"
            for device_name in devices:
                device = self.house.rooms[room_name].devices[device_name]
                actions = device.get_actions()
                context += f"  - Device: {device_name}\n"
                for action_name, action_info in actions.items():
                    context += f"    - Action: {action_name}\n"
                    context += f"      Description: {action_info.description}\n"
                    if action_info.parameters:
                        context += f"      Parameters:\n"
                        for param_name, param_info in action_info.parameters.items():
                            context += f"        - {param_name} ({param_info.type})\n"
                            context += f"          Description: {param_info.description}\n"
                            context += f"          Range: {param_info.range}\n"
        return context

    def process_command(self, user_input):
        system_prompt = "You are an AI assistant for home automation."
        context = self.build_context()

        task_prompt = f"""
{context}

User Input:
"{user_input}"

Instructions:
- Analyze the user input.
- Determine the appropriate command to execute based on the available devices and actions.
- Provide the result as a JSON object with the following fields:
  - target_room_name (string)
  - device_name (string)
  - action (string)
  - parameters (object, optional)
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_prompt}
        ]

        class CommandsOutputs(BaseModel):
            class CommandOutput(BaseModel):
                target_room_name: str = Field(..., description="The name of the room where the device is located.")
                device_name: str = Field(..., description="The name of the device to control.")
                action: str = Field(..., description="The action to perform on the device.")
                parameters: Optional[dict] = Field(default=None, description="Additional parameters for the action.")

            commands: list[CommandOutput] = Field(..., description="The list of commands to execute.")
            reasoning: str = Field(..., description="Provide a detailed reasoning for the commands that have to be run")

        client = openai.OpenAI()
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            response_format=CommandsOutputs,
        )

        result = response.choices[0].message.parsed  # Access the parsed command arguments

        # Now execute the command
        try:
            self.command_interface.execute(
                target_room_name=result.target_room_name,
                device_name=result.device_name,
                action=result.action,
                parameters=result.parameters or {}  # Use an empty dict if parameters is None
            )
            print(f"Assistant: Executed action '{result.action}' on device '{result.device_name}' in room '{result.target_room_name}'.")
        except Exception as e:
            print(f"Error executing command: {e}")
            print(f"Assistant: I'm sorry, I couldn't execute your command due to an error.")

        return result

    @staticmethod
    def load_house_state(filename):
        """Load the house state from a JSON file and recreate the house."""
        with open(filename, 'r') as f:
            house_data = json.load(f)

        # Recreate the house
        my_house = House()
        for room_data in house_data['rooms']:
            room = Room(name=room_data['room_name'])
            room.set_human_status(room_data['human_status']['status']['human_present'])
            for device_name, device_data in room_data['devices'].items():
                device_type = device_data['type']
                if device_type == 'Light':
                    device = Light(name=device_name)
                elif device_type == 'AirConditioner':
                    device = AirConditioner(name=device_name)
                else:
                    continue  # Skip unknown device types

                device.status = device_data['status']
                room.add_device(device)
            my_house.add_room(room)

        return my_house

def main():
    # Load the house state
    asset_dir = '/home/shreyas/NLP/llm-home-automation-analysis/llm_home_automation_analysis/src/dataset/asset'
    house_state_file = os.path.join(asset_dir, 'house_state.json')
    if not os.path.exists(house_state_file):
        print(f"House state file '{house_state_file}' not found.")
        return

    my_house = GPTAgent.load_house_state(house_state_file)
    command_interface = UserCommand(my_house)
    agent = GPTAgent(my_house, command_interface)

    # Load the natural language commands
    nl_commands_file = os.path.join(asset_dir, 'composite_commands.json')
    if not os.path.exists(nl_commands_file):
        print(f"Natural language commands file '{nl_commands_file}' not found.")
        return

    with open(nl_commands_file, 'r') as f:
        nl_commands = json.load(f)

    nl_commands = nl_commands['composite_commands']
    print(nl_commands)
    outs_dict = defaultdict(list)

    for idx, instruction in enumerate(nl_commands):
        print(f"\nProcessing command {idx+1}/{len(nl_commands)}:")
        print(f"Instruction: {instruction['input']}")
        result = agent.process_command(instruction['input'])
        inter_dict = {
            "instruction": instruction["input"],
            "ground_truth": instruction["output"],
            "result": result.model_dump()
        }
        outs_dict[instruction['input']].append(inter_dict)
        break

    # Write the results to a file
    with open(os.path.join(asset_dir, 'simple_gpt_results.json'), 'w') as f:
        json.dump(outs_dict, f, indent=2)

        

    # Resume capabilities
    # resume_file = os.path.join(asset_dir, 'agent_resume.json')
    # if os.path.exists(resume_file):
    #     with open(resume_file, 'r') as f:
    #         resume_data = json.load(f)
    #         start_index = resume_data.get('last_processed_index', 0)
    # else:
    #     start_index = 0

    # Process each natural language command
    # for idx in range(start_index, len(nl_commands)):
    #     # Extract the list of instructions
    #     natural_language_data = nl_commands[idx]['natural_language']
    #     instruction_list = natural_language_data[1]  # Assuming the structure is ["instructions", [list_of_instructions]]

    #     for nl_instruction in instruction_list:
    #         print(f"\nProcessing command {idx+1}/{len(nl_commands)}:")
    #         print(f"Instruction: {nl_instruction}")

    #         agent.process_command(nl_instruction)

    #         # Optionally, print the updated device status
    #         command = nl_commands[idx]['command']
    #         target_room = command['target_room_name']
    #         device_name = command['device_name']
    #         device_status = my_house.get_room_status(target_room)['devices'][device_name]
    #         print(f"Updated Status of '{device_name}' in '{target_room}': {device_status}")

    #         # Save resume data
    #         with open(resume_file, 'w') as f:
    #             json.dump({'last_processed_index': idx + 1}, f)

if __name__ == "__main__":
    main()