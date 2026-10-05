import getpass
import logging
from netmiko import ConnectHandler
from ntc_templates.parse import parse_output


logging.basicConfig(filename="logs/lab.log", level=logging.INFO)

def main():
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")

        logging.info("CREDENTIALS_COLLECTED")

        device = {
            "device_type": "cisco_ios",
            "host": "devnetsandboxiosxec8k.cisco.com",
            "username": username,
            "password": password,
        }

        try:
            connection = ConnectHandler(**device)
            print("Connected successfully!")
            logging.info("CONNNECT_OK")

            version_output = connection.send_command("show version")
            print(version_output)

            parsed_version = parse_output(
                platform="cisco_ios",
                command="show version",
                data=version_output
            )

            print(parsed_version)

            logging.info("PARSE_OK:show version")




            with open("data/raw/show_version.txt", "w") as file:
                file.write(version_output)
                

            interface_output = connection.send_command("show interfaces")
            print(interface_output)

            parsed_interfaces = parse_output(
                platform="cisco_ios",
                command="show interfaces",
                data=interface_output
            )

            print(parsed_interfaces)
            
            logging.info("PARSE_OK:show interfaces")


            
            with open("data/raw/show_interfaces.txt", "w") as file:
                file.write(interface_output)


            inventory_output = connection.send_command("show inventory")
            print(inventory_output)

            parsed_inventory = parse_output(
                platform="cisco_ios",
                command="show inventory",
                data=inventory_output
            )

            print(parsed_inventory)

            logging.info("PARSE_OK:show inventory")

            with open("data/raw/show_inventory.txt", "w") as file:
                file.write(inventory_output)

            hostname = parsed_version[0]["hostname"]
            version = parsed_version[0]["version"]
            model = parsed_inventory[0]["pid"]

            up_interfaces = 0
            down_interfaces = 0

            for interface in parsed_interfaces:
                if interface["link_status"] == "up":
                    up_interfaces += 1
                else:
                    down_interfaces += 1

            summary = f"""
        Device Summary
        Hostname: {hostname}
        Model: {model}
        IOS Version: {version}
        Interfaces Up: {up_interfaces}
        Interfaces Down: {down_interfaces}
        """
            
            print(summary)

            connection.disconnect()
            logging.info("DISCONNECT_OK")



        except Exception as error:
            print("Connection failed:", error)
            logging.info("CONNECT_FAIL")

if __name__ == "__main__":
    logging.info("LAB2_START")
    main()
    logging.info("LAB2_END")
