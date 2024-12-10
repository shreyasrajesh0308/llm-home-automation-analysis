from llm_home_automation_analysis.src.simulation.house import House
from llm_home_automation_analysis.src.simulation.room import Room
from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner
from llm_home_automation_analysis.src.simulation.user_command import UserCommand

def main():
    # Create devices
    light1 = Light(name="Living Room Light")
    ac1 = AirConditioner(name="Living Room AC")
    light2 = Light(name="Bedroom Light", brightness=75)
    ac2 = AirConditioner(name="Bedroom AC", temperature=22)

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

    # Create UserCommand instance
    command = UserCommand(my_house)

    # Set initial statuses using UserCommand
    command.execute(
        target_room_name="Living Room",
        device_name="Living Room Light",
        action="turn_on"
    )
    command.execute(
        target_room_name="Living Room",
        device_name="Living Room AC",
        action="turn_on"
    )
    command.execute(
        target_room_name="Living Room",
        device_name="Living Room AC",
        action="set_temperature",
        parameters={"temperature": 24}
    )
    living_room.set_human_status(is_present=True)

    command.execute(
        target_room_name="Bedroom",
        device_name="Bedroom Light",
        action="turn_off"
    )
    command.execute(
        target_room_name="Bedroom",
        device_name="Bedroom AC",
        action="turn_off"
    )
    bedroom.set_human_status(is_present=False)

    # Get and print room statuses
    living_room_status = my_house.get_room_status("Living Room")
    bedroom_status = my_house.get_room_status("Bedroom")

    print("Living Room Status:")
    print(living_room_status)
    print("\nBedroom Status:")
    print(bedroom_status)

    # Use UserCommand to interactively discover devices, actions, and parameters

    # List devices in the Bedroom
    devices_in_bedroom = command.list_devices("Bedroom")
    print("\nDevices in Bedroom:")
    print(devices_in_bedroom)

    # Get detailed actions for Bedroom Light
    actions_for_bedroom_light = command.list_device_actions("Bedroom", "Bedroom Light")
    print("\nDetailed Actions for 'Bedroom Light':")
    for action_name, action_details in actions_for_bedroom_light.items():
        print(f"Action: {action_name}")
        print(f"  Description: {action_details['description']}")
        if action_details['parameters']:
            print("  Parameters:")
            for param_name, param_info in action_details['parameters'].items():
                print(f"    {param_name}:")
                print(f"      Type: {param_info['type']}")
                print(f"      Range: {param_info['range']}")
                print(f"      Description: {param_info['description']}")
        else:
            print("  Parameters: None")
        print()

    # Execute 'set_brightness' action with correct parameters
    command.execute(
        target_room_name="Bedroom",
        device_name="Bedroom Light",
        action="set_brightness",
        parameters={"brightness": 85}
    )

    # Update human status in Bedroom
    bedroom.set_human_status(is_present=True)

    # Get and print updated room status
    updated_bedroom_status = my_house.get_room_status("Bedroom")
    print("\nUpdated Bedroom Status:")
    print(updated_bedroom_status)

if __name__ == "__main__":
    main()
