import json
import os
os.environ['HF_HOME'] = '/mnt/SSD1/chenda/cache/huggingface'
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from collections import defaultdict
import outlines
from outlines.samplers import greedy

import llama_cpp
from transformers import AutoTokenizer

# Import your simulation modules (adjust paths as necessary)
from llm_home_automation_analysis.src.simulation.house import House
from llm_home_automation_analysis.src.simulation.room import Room
from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner
from llm_home_automation_analysis.src.simulation.user_command import UserCommand
from huggingface_hub import login

# login(token="") # login to huggingface
# set huggingface cache dir


# Replace this with your system prompt as needed.
SYSTEM_PROMPT = "You are an AI assistant for home automation."


class CommandOutput(BaseModel):
    target_room_name: str = Field(..., description="The name of the room where the device is located.")
    device_name: str = Field(..., description="The name of the device to control.")
    action: str = Field(..., description="The action to perform on the device.")
    parameters: Optional[Dict] = Field(default=None, description="Additional parameters for the action.")

# New class for composite commands
class CompositeCommandOutput(BaseModel):
    commands: List[CommandOutput] = Field(..., description="A list of commands to be executed.")


class Agent:
    def __init__(self, house: House, command_interface: UserCommand, model_path, model_name, tokenizer_name):
        self.house = house
        self.command_interface = command_interface
        self.model, self.tokenizer = self.load_llamacpp_model_tokenizer(model_path, model_name, tokenizer_name)
        # Using outlines to generate JSON directly into a CommandOutput object
        self.generator = outlines.generate.json(self.model, CompositeCommandOutput, sampler=greedy())

    def load_llamacpp_model_tokenizer(self, model_path, model_name, tokenizer_name):
        """
        Load the QWEN model from llama_cpp and the tokenizer from Qwen/Qwen2.5-32B-Instruct.
        Modify paths as needed.
        """
        print(f"Loading {model_name} model...")
        model = outlines.models.llamacpp(
            model_path,
            model_name,
            tokenizer=llama_cpp.llama_tokenizer.LlamaHFTokenizer.from_pretrained(tokenizer_name),
            n_gpu_layers=-1,
            verbose=False
        )
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        return model, tokenizer

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

    def create_prompt(self, user_input: str) -> str:
        context = self.build_context()

        # We structure the messages for apply_chat_template
        # The assistant role here will be generated by the model, so we leave it empty
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
{context}

User Input:
\"{user_input}\"

Instructions:
- Analyze the user input.
- Determine the appropriate command to execute based on the available devices and actions.
- Return a list of commands, if multiple commands are needed, include them all.
- Provide the result as a list of JSON object with the following fields:
  - target_room_name (string)
  - device_name (string)
  - action (string)
  - parameters (object, optional)
"""
            },
            {
                "role": "assistant",
                "content": ""
            }
        ]

        # Convert these messages into a text prompt using the tokenizer's template method
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        return prompt

    def process_command(self, user_input: str):
        prompt = self.create_prompt(user_input)

        # Generate structured output that directly returns a CommandOutput object
        try:
            result = self.generator(prompt)
        except Exception as e:
            print(f"Error generating structured response: {e}")
            print("Assistant: I couldn't produce a valid command.")
            return

        # Execute the command
        try:
            for cmd in result.commands:
                self.command_interface.execute(
                    target_room_name=cmd.target_room_name,
                    device_name=cmd.device_name,
                    action=cmd.action,
                    parameters=cmd.parameters or {}
                )
                print(f"Assistant: Executed action '{cmd.action}' on device '{cmd.device_name}' in room '{cmd.target_room_name}'.")
        except Exception as e:
            print(f"Error executing command: {e}")
            print("Assistant: I'm sorry, I couldn't execute your command due to an error.")
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


def main(model_path, model_name, tokenizer_name, house_state_file, nl_commands_file, result_folder):
    # Load the house state
    if not os.path.exists(house_state_file):
        print(f"House state file '{house_state_file}' not found.")
        return

    my_house = Agent.load_house_state(house_state_file)
    command_interface = UserCommand(my_house)
    agent = Agent(my_house, command_interface, model_path, model_name, tokenizer_name)

    # Load the natural language commands
    if not os.path.exists(nl_commands_file):
        print(f"Natural language commands file '{nl_commands_file}' not found.")
        return

    with open(nl_commands_file, 'r') as f:
        nl_commands = json.load(f)

    # Resume capabilities
    # resume_file = 'asset/agent_resume.json'
    # if os.path.exists(resume_file):
    #     with open(resume_file, 'r') as f:
    #         resume_data = json.load(f)
    #         start_index = resume_data.get('last_processed_index', 0)
    # else:
    start_index = 0
    print("=========nl_commands: ", nl_commands.keys())
    for command_level, sub_nl_commands in nl_commands.items():
        print("=========command_level: ", command_level)
        # print("=========command_list: ", nl_commands)
        # Process each natural language command
        outs_dict = defaultdict(list)

        for idx, instruction in enumerate(sub_nl_commands):
            print(f"\nProcessing command {idx+1}/{len(sub_nl_commands)}:")
            print(f"Instruction: {instruction['input']}")
            result = agent.process_command(instruction['input'])
            inter_dict = {      
                    "instruction": instruction["input"],
                    "ground_truth": instruction["output"],
                    "result": result.model_dump()
            }
            outs_dict[instruction['input']].append(inter_dict)
        os.makedirs(os.path.join(result_folder, model_name), exist_ok=True)
        with open(os.path.join(result_folder, model_name, f"{command_level}.json"), 'w') as f:
            json.dump(outs_dict, f, indent=2)


if __name__ == "__main__":
    # model_path =  "bartowski/Qwen2.5-32B-Instruct-GGUF"
    # model_name = "Qwen2.5-32B-Instruct-Q5_K_S.gguf"
    # tokenizer_name = "Qwen/Qwen2.5-32B-Instruct"
    
    model_path = "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF"
    model_name = "Meta-Llama-3.1-8B-Instruct-f32.gguf"
    tokenizer_name = "meta-llama/Llama-3.1-8B-Instruct"
    
    # model_path = "bartowski/Llama-3.2-1B-Instruct-GGUF"
    # model_name = "Llama-3.2-1B-Instruct-f16.gguf"
    # tokenizer_name = "meta-llama/Llama-3.2-1B-Instruct"

    house_state_file = 'asset/house_state.json'
    nl_commands_file = 'llm_home_automation_analysis/src/dataset/data/composite_commands.json'
    result_folder = "llm_home_automation_analysis/src/dataset/result"
    os.makedirs(result_folder, exist_ok=True)
    main(model_path, model_name, tokenizer_name, house_state_file, nl_commands_file, result_folder)
