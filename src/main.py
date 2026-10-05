import logging
from netmiko import ConnectHandler
from ntc_templates.parse import parse_output
from paramiko.ssh_exception import AuthenticationException
from netmiko.exceptions import NetmikoTimeoutException
from paramiko.ssh_exception import AuthenticationException, SSHException
import getpass
logging.basicConfig(filename="logs/lab.log", level=logging.INFO)

def main():
    logging.info("[STEP 2] Dev Container Started")

    username = input("Enter your username: ").strip()
    password = getpass.getpass("Enter your password: ")

    logging.info("CREDENTIALS_COLLECTED")

    device = {
        "device_type": "cisco_ios",
        "host": "devnetsandboxiosxec8k.cisco.com",
        "username": username,
        "password": password,
        "port": 22,
        "secret": password,
        "timeout": 10}


    try:

        net_connect = ConnectHandler(**device)
        logging.info("CONNECT_OK")
        
    except AuthenticationException:
        logging.info("CONNECT_FAIL")

    except NetmikoTimeoutException:
        logging.info("CONNECT_FAIL")

    except SSHException:
        logging.info("CONNECT_FAIL")

    except Exception:
        logging.info("CONNECT_FAIL")

    else:
        interface_output = net_connect.send_command("show ip interface brief")
        logging.info("CMD_RUN: show ip interace brief")
        with open("data/raw/show_ip_interface_brief.txt","w") as file:
            file.write(interface_output)

        version_output = net_connect.send_command('show version')
        logging.info("CMD_RUN: show version")
        with open("data/raw/show_version.txt", "w") as file:
            file.write(version_output)

        inventory_output = net_connect.send_command("show inventory")
        logging.info("CMD_RUN: show inventory")
        with open("data/raw/show_inventory.txt", "w") as file:
            file.write(inventory_output)

        try:
            parsed_output = parse_output(
            platform="cisco_ios", 
            command="show ip interface brief",
            data=interface_output)

            print(parsed_output)

        except Exception:
            logging.info("PARSE_FAIL:show ip interface brief")

        else:
            if parsed_output:
                logging.info("PARSE_OK:show ip interface brief")
            else:
                logging.info("PARSE_FAIL:show ip interface brief")

        try:
            parsed_version = parse_output(
            platform="cisco_ios", 
            command="show version",
            data=version_output)

            print(parsed_version)

        except Exception:
                logging.info("PARSE_FAIL:show version")
        else:
                if parsed_version:
                    logging.info("PARSE_OK:show version")
                else:
                    logging.info("PARSE_FAIL:show version")

        try:
            parsed_inventory = parse_output(
                platform="cisco_ios",
                command="show inventory",
                data=inventory_output
            )
            print(parsed_inventory)
        except Exception:
            logging.info("PARSE_FAIL:show inventory")
        else:
            if parsed_inventory:
                logging.info("PARSE_OK:show inventory")
            else:
                logging.info("PARSE_FAIL:show inventory")

        device_info = parsed_version[0]
        report = f"Hostname: {device_info['hostname']}\n"
        report += f"Model: {device_info['hardware'][0]}\n"
        report += f"Software version: {device_info['version']}\n"
        report += "\nInterfaces:\n"

        for interface in parsed_output:
            report += (
            f"{interface['interface']} | "
            f"IP: {interface['ip_address']} | "
            f"Status: {interface['status']} | "
            f"Protocol: {interface['proto']}\n"
            )
        print(report)
        logging.info("REPORT_SAVED)")
        net_connect.disconnect()

if __name__ == "__main__":
    logging.info("LAB2-START")
    main()
    logging.info("LAB2-END")
    

