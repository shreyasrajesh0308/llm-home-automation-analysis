from llm_home_automation_analysis.src.simulation.house import House
from llm_home_automation_analysis.src.simulation.room import Room
from llm_home_automation_analysis.src.simulation.device import Light, AirConditioner
from llm_home_automation_analysis.src.simulation.user_command import User_Command

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

    # Set initial statuses
    living_room.set_human_status(is_present=True)
    living_room.set_device_status("Living Room Light", True)
    living_room.set_device_status("Living Room AC", True)
    ac1.set_temperature(24)

    bedroom.set_human_status(is_present=False)
    bedroom.set_device_status("Bedroom Light", False)
    bedroom.set_device_status("Bedroom AC", False)

    # Get and print room statuses
    living_room_status = my_house.get_room_status("Living Room")
    bedroom_status = my_house.get_room_status("Bedroom")

    print("Living Room Status:")
    print(living_room_status)
    print("\nBedroom Status:")
    print(bedroom_status)

    # Change statuses
    my_house.set_room_status("Bedroom", device_name="Bedroom Light", device_status=True)
    my_house.set_room_status("Bedroom", human_status=True)

    # Get and print updated room statuses
    updated_bedroom_status = my_house.get_room_status("Bedroom")
    print("\nUpdated Bedroom Status:")
    print(updated_bedroom_status)
    
    print("\n--- Executing Instructions ---\n")

    # 1. User in Living Room turns on the Bedroom Light
    Instruction1 = User_Command(
        source_room=living_room,
        target_room=bedroom,
        action="turn on light"
    )
    Instruction1.execute()

    # 2. User in Bedroom sets the temperature to 22°C
    Instruction2 = User_Command(
        source_room=bedroom,
        target_room=bedroom,
        action="set temperature",
        parameters={'temperature': 22}
    )
    Instruction2.execute()

    # 3. User in Hallway (assuming hallway exists) requests status of Living Room
    # Since Hallway is not defined in the original setup, we'll create it
    hallway = Room(name="Hallway")
    my_house.add_room(hallway)

    Instruction3 = User_Command(
        source_room=hallway,
        target_room=living_room,
        action="report status"
    )
    status = Instruction3.execute()
    print("\nStatus Report from Instruction:")
    print(status)

    # 4. User in Bedroom turns off the Living Room AC
    Instruction4 = User_Command(
        source_room=bedroom,
        target_room=living_room,
        action="turn off light"  # Assuming you want to turn off the light
    )
    Instruction4.execute()

    # 5. User in Living Room sets the Bedroom Light brightness to 50%
    Instruction5 = User_Command(
        source_room=living_room,
        target_room=bedroom,
        action="set brightness",
        parameters={'brightness': 50}
    )
    Instruction5.execute()

    # Get and print updated room statuses
    print("\n--- Updated Room Statuses ---\n")
    updated_living_room_status = my_house.get_room_status("Living Room")
    updated_bedroom_status = my_house.get_room_status("Bedroom")

    print("Living Room Status:")
    print(updated_living_room_status)
    print("\nBedroom Status:")
    print(updated_bedroom_status)

if __name__ == "__main__":
    main()
