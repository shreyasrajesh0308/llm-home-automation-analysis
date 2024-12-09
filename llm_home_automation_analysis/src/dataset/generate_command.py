# Assuming the necessary imports from your modules
import json
import random
from llm_home_automation_analysis.src.simulation.house import House
from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner
from llm_home_automation_analysis.src.simulation.room import Room
from llm_home_automation_analysis.src.simulation.user_command import User_Command

def generate_all_possible_commands(house):
    """Generates all possible commands based on the house configuration."""
    commands = []
    actions = ["turn on light", "turn off light", "set temperature", "set brightness", "report status"]

    # Define specific temperature and brightness values
    temperature_values = [16, 31]  # Representing cold and hot
    brightness_values = [10, 90]   # Representing dim and bright

    # Generate all combinations of source rooms, target rooms, actions
    source_rooms = house.rooms
    target_rooms = house.rooms

    for source_room in source_rooms:
        for target_room in target_rooms:
            for action in actions:
                parameters = {}
                if action == "set temperature":
                    for temp in temperature_values:
                        parameters = {'temperature': temp}
                        command = {
                            'source_room': source_room.name,
                            'target_room': target_room.name,
                            'action': action,
                            'parameters': parameters
                        }
                        commands.append(command)
                elif action == "set brightness":
                    for brightness in brightness_values:
                        parameters = {'brightness': brightness}
                        command = {
                            'source_room': source_room.name,
                            'target_room': target_room.name,
                            'action': action,
                            'parameters': parameters
                        }
                        commands.append(command)
                else:
                    # Actions without parameters
                    command = {
                        'source_room': source_room.name,
                        'target_room': target_room.name,
                        'action': action,
                        'parameters': parameters
                    }
                    commands.append(command)
    return commands


def main(json_path, debug=False):

    # Create devices
    light1 = Light(name="Living Room Light")
    ac1 = AirConditioner(name="Living Room AC")
    light2 = Light(name="Bedroom Light")
    ac2 = AirConditioner(name="Bedroom AC")

    # Create rooms and add devices
    living_room = Room(name="Living Room")
    living_room.add_device(light1)
    living_room.add_device(ac1)

    bedroom = Room(name="Bedroom")
    bedroom.add_device(light2)
    bedroom.add_device(ac2)

    # Create house and add rooms
    my_house = House()
    my_house.add_room(living_room)
    my_house.add_room(bedroom)

    # Generate all possible commands
    all_commands = generate_all_possible_commands(my_house)

    # Print total number of commands
    print(f"Total number of commands generated: {len(all_commands)}")

    if debug:
        for idx, command in enumerate(all_commands):
            print(f"\nCommand {idx+1}:")
            print(json.dumps(command, indent=2))

    # Save commands to a JSON file
    with open(json_path, 'w') as f:
        json.dump(all_commands, f, indent=2)
        print(f"\nAll commands saved to {json_path}")
if __name__ == "__main__":
    json_path = "/Users/duanchenda/Desktop/gitplay/llm-home-automation-analysis/asset/house_dataset.json"
    main(json_path)
