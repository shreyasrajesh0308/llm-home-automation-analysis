import json
import openai
import os
from openai import OpenAI

# Create an OpenAI client instance
client = OpenAI(
)
def load_commands(filename):
    """Loads commands from a JSON file."""
    with open(filename, 'r') as f:
        commands = json.load(f)
    return commands

def generate_natural_language_command(command,num_variations=3):
    """Generates a human language command using OpenAI's GPT-3.5-turbo model."""
    # Create a system message to instruct the assistant
    system_message = {
    "role": "system",
    "content": (
        "You are an assistant that converts structured home automation commands into natural language instructions. "
        "Each command includes the following fields:\n"
        "- 'source_room': The room from which the command originates.\n"
        "- 'target_room': The room where the action should be performed.\n"
        "- 'action': The action to perform (e.g., 'turn on light', 'set temperature').\n"
        "- 'parameters': Additional parameters required for the action (e.g., {'temperature': 16}).\n\n"
        "Your task is to generate a list of polite, natural-sounding commands that a user in the 'source_room' might say to perform the 'action' in the 'target_room'. "
        "Include both direct requests and indirect expressions (e.g., expressions of feeling). "
        "Ensure each command is concise and uses appropriate language for the given action and parameters.\n\n"
        "For example, if the command is:\n"
        "{\n"
        "  'source_room': 'Living Room',\n"
        "  'target_room': 'Living Room',\n"
        "  'action': 'set temperature',\n"
        "  'parameters': {'temperature': 16}\n"
        "}\n"
        "You might generate:\n"
        "- 'Please set the temperature to 16 degrees.'\n"
        "- 'It's a bit warm in here; could you lower the temperature?'\n"
        "- 'I'm feeling hot!'\n\n"
        "Use similar phrasing and adjust pronouns like 'here' or 'in the [room name]' based on whether the 'source_room' and 'target_room' are the same."
    )
}


    # Create a user message with the command data
    user_message = {
        "role": "user",
        "content": f"Convert the following command to natural language instructions:\n{json.dumps(command, indent=2)}"
    }
    messages = [system_message, user_message]

    # Call the OpenAI API using the client
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=60,
            temperature=0.7,
            n=num_variations,  # Request multiple variations
        )
        
        # Extract all assistant replies
        responses = []
        for choice in chat_completion.choices:
            assistant_reply = choice.message.content.strip()
            # Split responses if the assistant returns multiple lines
            variations = [resp.strip("- ").strip() for resp in assistant_reply.split("\n") if resp.strip()]
            responses.extend(variations)
        
        return responses
    except Exception as e:
        print(f"Error generating natural language commands: {e}")
        return []

def main(command_path, save_path):
    # Load the commands from the JSON file
    commands = load_commands(command_path)
    print(f"Total commands to process: {len(commands)}")

    # List to hold the results
    results = []

    # Process each command
    for idx, command in enumerate(commands):
        print(f"Processing command {idx+1}/{len(commands)}...")

        # Generate the natural language command
        nl_command = generate_natural_language_command(command)

        if nl_command:
            # Append the result to the list
            result = {
                'command': command,
                'natural_language': nl_command
            }
            results.append(result)
        else:
            print(f"Failed to generate natural language command for command {idx+1}.")

    # Save the results to a new JSON file
    with open(save_path, 'w') as f:
        json.dump(results, f, indent=2)
        print(f"Results saved to {save_path}.")

if __name__ == '__main__':
    command_path = "/Users/duanchenda/Desktop/gitplay/llm-home-automation-analysis/asset/house_dataset.json"
    save_path = command_path.replace(".json", "_with_natural_language.json")
    main(command_path, save_path)