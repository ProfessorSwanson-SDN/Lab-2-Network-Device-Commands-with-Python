import getpass 
import logging
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException
from paramiko.ssh_exception import AuthenticationException, SSHException

import json
from ntc_templates.parse import parse_output

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    filename="logs/lab.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    logging.info("[CREDENTIALS_COLLECTED]")

    host = input("Enter Cisco sandbox hostname or IP: ").strip()
    connection = None

    try:
        connection = ConnectHandler(
            device_type="cisco_ios",
            host=host,
            username=username,
            password=password,
            port=22,
        )

        prompt = connection.find_prompt()
        print(f"Connected to device: {prompt}")
        logging.info("[CONNECT_OK]")

        logging.info("[CONNECT_OK]")

        Path("data/raw").mkdir(parents=True, exist_ok=True)

        commands = [
        "show version",
        "show ip interface brief",
        "show inventory",
        ]

        for command in commands:
            output = connection.send_command(command)
            logging.info("[CMD_RUN] CMD_RUN: %s", command)

            filename = command.replace(" ", "_") + ".txt"
            filepath = Path("data/raw") / filename
            filepath.write_text(output, encoding="utf-8")

            print(f"Saved {command} output to {filepath}")

        try:
            parsed_data = parse_output(
            platform="cisco_ios",
            command=command,
            data=output,
            )

            if not isinstance(parsed_data, (list, dict)) or not parsed_data:
                raise ValueError("Parsed output is empty or invalid")

            Path("data/reports").mkdir(parents=True, exist_ok=True)

            parsed_filename = command.replace(" ", "_") + ".json"
            parsed_filepath = Path("data/reports") / parsed_filename

            parsed_filepath.write_text(
                json.dumps(parsed_data, indent=4),
                encoding="utf-8",
            )

            logging.info("[PARSE_OK] PARSE_OK:%s, command")
            print(f"Parsed {command}:")
            print(json.dumps(parsed_data, indent=4))
    
        except Exception as error:
            logging.error(
            "[PARSe_FAIL] PARSE_FAIL:%s (%s)",
            command,
            type(error).__name__,
            )
            print(f"Could not parse {command}: {error}")

            version_path = Path("data/reports/show_version.json")
            interfaces_path =("data/reports/show_ip_interface_brief.json")
    
            version_data = json.loads(version_path.read_text(encoding="utf-8"))
            interfaces = json.loads(interfaces_path.read_text(encoding="utf-8"))
    
            device = version_data[0]
    
            hostname = device.get("hostname", "Unknown")
            model = device.get("hardware", "Unknown")
            version = device.get("version", "Unknown")
    
            if isinstance(model, list):
                model = ", ".join(model)
    
            summary = (
                f"Device Summary\n"
                f"Hostname: {hostname}\n"
                f"Model: {model}\n"
                f"IOS Version: {version}\n\n"
                f"Interface States\n"
            )
    
            for interface in interfaces:
                summary += (
                    f"{interface.get('interface', 'Unknown')}: "
                    f"IP {interface.get('ip_address', 'Unknown')}, "
                    f"Status {interface.get('status', 'Uknown')}, "
                    f"Protocol {interface.get('proto', 'Unknown')}\n"
                )
    
            print(summary)
    
            report_path = Path("data/reports/device_summary.txt")
            report_path.write_text(summary, encoding="utf-8")
    
            logging.info("[REPORT_SAVED]")
            print(f"Report saved to {report_path}")

    

        except AuthenticationException:
            print("Authentication failed. Please check your username and password.")
            logging.error("[CONNECT_FAIL] Authentication failed.")

        except NetmikoTimeoutException:
            print("Connection timed out. Check the sandbox host and connectivity.")
            logging.error("[CONNECT_FAIL] Connection timed out.")

        except SSHException:
            print("An SSH connection error occured.")
            logging.error("[CONNECT_FAIL] SSH error.")

        except Exception as error:
            print(f"Connection failed: {type(error).__name__}")
            logging.error("[CONNECT_FAIL] %s", type(error).__name__)

    finally:
        if connection is not None:
            connection.disconnect()

if __name__ == "__main__":
    logging.info("[LAB2-START] [LAB2_START]")
    try:
        main()
    finally:
        logging.info("[LAB2-END] [LAB2_END]")