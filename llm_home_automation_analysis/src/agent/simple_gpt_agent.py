import json
import os
os.environ['HF_HOME'] = '/mnt/SSD1/chenda/cache/huggingface'
from pydantic import BaseModel, Field
import openai
from typing import Optional
from collections import defaultdict
from textwrap import dedent
import time

import outlines
from outlines.samplers import greedy
import llama_cpp
from transformers import AutoTokenizer

from llm_home_automation_analysis.src.simulation.house import House
from llm_home_automation_analysis.src.simulation.room import Room
from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner
from llm_home_automation_analysis.src.simulation.user_command import UserCommand
from llm_home_automation_analysis.src.prompts.prompts import build_prompt, GPTAgentPrompt
from llm_home_automation_analysis.src.prompts.prompts import CommandsOutputsWithReasoning, CommandsOutputs



class GPTAgent:
    def __init__(self, house, command_interface, model_name):
        self.house = house
        self.command_interface = command_interface
        self.model_name = model_name

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
        context = self.build_context()

        messages = [
            {"role": "system", "content": GPTAgentPrompt.system_prompt},
            {"role": "user", "content": dedent(build_prompt(context=context, user_input=user_input))}
        ]


        client = openai.OpenAI()
        response = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=messages,
            temperature=0,
            response_format=CommandsOutputsWithReasoning,
        )

        result = response.choices[0].message.parsed  # Access the parsed command arguments

        return result, context

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
    

class OpenSourceAgent:
    def __init__(self, house: House, command_interface: UserCommand, model_path, model_name, tokenizer_name):
        self.house = house
        self.command_interface = command_interface
        self.model, self.tokenizer = self.load_llamacpp_model_tokenizer(model_path, model_name, tokenizer_name)
        self.model_name = model_name
        # Using outlines to generate JSON directly into a CommandOutput object
        self.generator = outlines.generate.json(self.model, CommandsOutputsWithReasoning, sampler=greedy())

    def load_llamacpp_model_tokenizer(self, model_path, model_name, tokenizer_name):
        """
        Load the required GGUF model and tokenizer.
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

    def create_prompt(self, context: str, user_input: str) -> str:

        messages = [
            {
                "role": "system",
                "content": GPTAgentPrompt.system_prompt
            },
            {
                "role": "user",
                "content": dedent(build_prompt(context=context, user_input=user_input))
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

        context = self.build_context()
        prompt = self.create_prompt(context, user_input)

        # Generate structured output that directly returns a CommandOutput object
        try:
            result = self.generator(prompt)
        except Exception as e:
            print(f"Error generating structured response: {e}")
            print("Assistant: I couldn't produce a valid command.")
            return None, context


        return result, context
        # Execute the command
        # try:
        #     for cmd in result.commands:
        #         self.command_interface.execute(
        #             target_room_name=cmd.target_room_name,
        #             device_name=cmd.device_name,
        #             action=cmd.action,
        #             parameters=cmd.parameters or {}
        #         )
        #         print(f"Assistant: Executed action '{cmd.action}' on device '{cmd.device_name}' in room '{cmd.target_room_name}'.")
        # except Exception as e:
        #     print(f"Error executing command: {e}")
        #     print("Assistant: I'm sorry, I couldn't execute your command due to an error.")

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
    asset_dir = '/home/shreyas/NLP/llm-home-automation-analysis/llm_home_automation_analysis/src/dataset/data'
    house_state_file = os.path.join(asset_dir, 'house_state.json')
    if not os.path.exists(house_state_file):
        print(f"House state file '{house_state_file}' not found.")
        return
    
    # model_names = ["gpt-4o-mini", "Qwen2.5-32B-Instruct", "llama-3.2-1B-Instruct", "Meta-Llama-3.1-8B-Instruct"]
    model_names = ["gpt-4o-mini"]

    command_files = ["simple_commands.json", "complex_commands.json", "composite_commands.json"]
    command_fields = ["simple_commands", "complex_commands", "composite_commands"]



    for model_name in model_names:

        print(f"Processing {model_name}...")

        if model_name == "gpt-4o-mini":
            my_house = GPTAgent.load_house_state(house_state_file)
            command_interface = UserCommand(my_house)
            agent = GPTAgent(my_house, command_interface, model_name)
            save_paths = ["simple_gpt_results.json", "complex_gpt_results.json", "composite_gpt_results.json"]

        elif model_name == "llama-3.2-1B-Instruct":
            model_path = "bartowski/Llama-3.2-1B-Instruct-GGUF"
            model_name = "Llama-3.2-1B-Instruct-f16.gguf"
            tokenizer_name = "meta-llama/Llama-3.2-1B-Instruct"
            my_house = OpenSourceAgent.load_house_state(house_state_file)
            command_interface = UserCommand(my_house)
            agent = OpenSourceAgent(my_house, command_interface, model_path, model_name, tokenizer_name)
            save_paths = ["simple_llama1B_results.json", "complex_llama1B_results.json", "composite_llama1B_results.json"]

        elif model_name == "Qwen2.5-32B-Instruct":
            model_path = "bartowski/Qwen2.5-32B-Instruct-GGUF"
            model_name = "Qwen2.5-32B-Instruct-Q5_K_S.gguf"
            tokenizer_name = "Qwen/Qwen2.5-32B-Instruct"
            my_house = OpenSourceAgent.load_house_state(house_state_file)
            command_interface = UserCommand(my_house)
            agent = OpenSourceAgent(my_house, command_interface, model_path, model_name, tokenizer_name)
            save_paths = ["simple_qwen32B_results.json", "complex_qwen32B_results.json", "composite_qwen32B_results.json"]

        elif model_name == "Meta-Llama-3.1-8B-Instruct":
            model_path = "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF"
            model_name = "Meta-Llama-3.1-8B-Instruct-f32.gguf"
            tokenizer_name = "meta-llama/Llama-3.1-8B-Instruct"
            my_house = OpenSourceAgent.load_house_state(house_state_file)
            command_interface = UserCommand(my_house)
            agent = OpenSourceAgent(my_house, command_interface, model_path, model_name, tokenizer_name)
            save_paths = ["simple_llama31_results.json", "complex_llama31_results.json", "composite_llama31_results.json"]



        times = []
        avg_times = []

        for command_file, command_field, save_path in zip(command_files, command_fields, save_paths):
            # Load the natural language commands
            nl_commands_file = os.path.join(asset_dir, command_file)
            if not os.path.exists(nl_commands_file):
                print(f"Natural language commands file '{nl_commands_file}' not found.")
                return

            with open(nl_commands_file, 'r') as f:
                nl_commands = json.load(f)

            nl_commands = nl_commands[command_field]

            results = []  # Changed from outs_dict

            # Add latency analysis 
            start_time_global = time.time()

            for idx, instruction in enumerate(nl_commands):


                start_time = time.time()
                print(f"\nProcessing command {idx+1}/{len(nl_commands)}:")
                print(f"Instruction: {instruction['input']}")
                result, context = agent.process_command(instruction['input'])
                results.append({
                    "instruction": instruction["input"],
                    "ground_truth": instruction["output"],
                    "result": result.model_dump(),
                    "context": context
                })

                end_time = time.time()
                print(f"Time taken for {idx+1} command: {end_time - start_time} seconds")

            end_time_global = time.time()
            print(f"Total time taken: {end_time_global - start_time_global} seconds")
            times.append(end_time_global - start_time_global)
            print(f"Average time per command: {(end_time_global - start_time_global) / len(nl_commands)} seconds")
            avg_times.append((end_time_global - start_time_global) / len(nl_commands))
            # Write the results to a file
            with open(os.path.join(asset_dir, save_path), 'w') as f:
                json.dump(results, f, indent=2)

        print(f"Average time taken for {model_name}: {sum(times) / len(times)} seconds")
        print(f"Average time per command for {model_name}: {sum(avg_times) / len(avg_times)} seconds")


if __name__ == "__main__":
    main()