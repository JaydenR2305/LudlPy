# Jayden Roberts
# 8/8/22

from collections.abc import Sequence
import serial
from typing import Optional, Union


_default_communication_parameters = {
    "baudrate": 9600,  # This number varies from model to model.
    # If you find that the provided example code doesn't run properly try other baud rates such as 19200
    "bytesize": serial.EIGHTBITS,
    "parity": serial.PARITY_NONE,
    "stopbits": serial.STOPBITS_TWO,
}

_cast_functions = {
    "float": float,
    "int": int,
    "string": str
}


class Controller:
    def __init__(self, serial_port_name: str) -> None:
        self.stage_port = self._register_port(serial_port_name)

    @staticmethod
    def _register_port(serial_port_name: str) -> serial.Serial:
        """

        :param serial_port_name: The name of the COM port to be used. Acceptable names include "COM2", "COM3", etc.
        :return: The instantiated serial object.
        """
        port_connection = serial.Serial(
            port=serial_port_name, **_default_communication_parameters
        )

        return port_connection

    @staticmethod
    def _format_command_string(command: str) -> bytes:
        """
        This function is used to convert the input command into a readable format for the controller.
        This is accomplished by adding a carriage return to the end of the command string,
        and converting the string to binary using the ASCII standard.

        :param command: The command string to be written to the buffer.
        :return: The binary command string in ASCII formatting.
        """
        carriage_command = f"{command}\r"
        return carriage_command.encode("ASCII")

    @staticmethod
    def _format_response(response_arguments: list[str], response_types: Sequence[str]):
        """
        :param response_arguments: The response from the controller in list format
        :param response_types: The types to cast the response_arguments to
        :return: The formatted array
        """
        assert len(response_arguments) == len(response_types), \
            "Response types must be equal in length to response arguments"

        formatted_response = []

        for response_argument, response_type in zip(response_arguments, response_types):
            formatted_response.append(_cast_functions[response_type](response_argument))

        return formatted_response

    def await_response(self, response_types: Optional[Sequence[str]] = None, response_has_newline: bool = True) \
            -> Union[tuple[bool, Optional[list]], str]:
        """
        Return the response from some command.

        :param response_types: An optional sequence containing the requested types to cast for response arguments.
        For example, we would want an integer when reading out a speed
        :param response_has_newline: A boolean indicating
        :return: The response from the controller in a list form.
        """
        while True:
            if self.stage_port.in_waiting > 0:
                if not response_has_newline:
                    response = self.stage_port.read()
                else:
                    response = self.stage_port.readline()

                response = response.decode("ASCII")

                # Some commands return a single character response.
                # These commands do not end with a newline and do not contain a reply character.
                if not response_has_newline:
                    return response

                response_array = response.split(" ")

                reply_character = response_array[0]

                if reply_character == ":A":
                    executed_successfully = True
                elif reply_character == ":N":
                    executed_successfully = False
                else:
                    raise Exception(f"Unknown reply character: {reply_character}")

                if response_has_newline:
                    # Remove the reply character from the start of the list and the newline character at the end of
                    # the list
                    response_array = response_array[1:-1]

                if executed_successfully and response_types:
                    response_array = self._format_response(response_array, response_types)

                return executed_successfully, response_array

    def send_check(self, motor_id: str = "X") -> tuple[bool, Optional[list]]:
        """
        Ensure the connection to the controller has been established successfully.

        :param motor_id: Which stage dimension to use. Currently, "X" & "Y" are supported.
        :return: See await_response()
        """
        self.stage_port.write(self._format_command_string(f"RDSTAT {motor_id}"))

        return self.await_response()

    def get_speed(self, motor_ids: Sequence[str]) -> tuple[bool, Optional[list[int]]]:
        """
        :param motor_ids: The motors to read speeds from
        :return: A bool indicating whether execution was successful,
        as well as a list of speeds from the requested motors.
        """
        self.stage_port.write(self._format_command_string(f"SPEED {' '.join(motor_ids)}"))

        response_types = ["int"]*len(motor_ids)
        response = self.await_response(response_types)

        return response

    def set_speed(self, motor_id_speed_dictionary: dict[str, int]) -> tuple[bool, Optional[list]]:
        """
        :param motor_id_speed_dictionary: A dictionary containing id - speed key value pairs
        :return: A bool indicating whether execution was successful.
        The response body is empty for a successful execution.
        """
        motor_parameters = [f"{motor_id} = {speed}" for motor_id, speed in motor_id_speed_dictionary.items()]

        self.stage_port.write(self._format_command_string(f"SPEED {' '.join(motor_parameters)}"))

        return self.await_response()

    def get_acceleration(self, motor_ids: Sequence[str]) -> tuple[bool, Optional[list[int]]]:
        """
        See get_speed()
        """
        self.stage_port.write(self._format_command_string(f"ACCEL {' '.join(motor_ids)}"))

        response_types = ["int"]*len(motor_ids)
        response = self.await_response(response_types)

        return response

    def set_acceleration(self, motor_id_acceleration_dictionary: dict[str, int]) -> tuple[bool, Optional[list]]:
        """
        See set_speed()
        """
        motor_parameters = [f"{motor_id} = {speed}" for motor_id, speed in motor_id_acceleration_dictionary.items()]

        self.stage_port.write(self._format_command_string(f"ACCEL {' '.join(motor_parameters)}"))

        return self.await_response()

    def get_absolute_position(self, motor_ids: Sequence[str]) -> tuple[bool, list[int]]:
        """
        Get the current position of the stage
        
        :param motor_ids: The motors to read the position from
        :return: A bool indicating whether execution was successful,
        as well as a list of positions from the requested motors.
        """
        self.stage_port.write(self._format_command_string(f"WHERE {' '.join(motor_ids)}"))

        response_types = ["int"]*len(motor_ids)
        response = self.await_response(response_types)

        return response
    
    def move_absolute(self, motor_id_position_dictionary: dict[str, int]) -> tuple[bool, Optional[list]]:
        """
        Move to the given coordinates in the absolute frame.

        :param motor_id_position_dictionary: A dictionary containing id - coordinate pairs.
        :return: A bool indicating whether execution was successful.
        The response body is empty for a successful execution.
        """
        motor_parameters = [f"{motor_id} = {position}" for motor_id, position in motor_id_position_dictionary.items()]

        self.stage_port.write(self._format_command_string(f"MOVE {' '.join(motor_parameters)}"))

        return self.await_response()

    def move_relative(self, motor_id_position_dictionary: dict[str, int]) -> tuple[bool, Optional[list]]:
        """
        Move to a given position relative to the current position.

        :param motor_id_position_dictionary: A dictionary containing id - coordinate pairs.
        :return: A bool indicating whether execution was successful.
        The response body is empty for a successful execution.
        """
        motor_parameters = [f"{motor_id} = {position}" for motor_id, position in motor_id_position_dictionary.items()]

        self.stage_port.write(self._format_command_string(f"MOVREL {' '.join(motor_parameters)}"))

        return self.await_response()

    def check_motor_status(self) -> tuple[bool, Optional[list]]:
        """
        Returns the status of the motors.
        "B" means the motors are still running and "N" means the motors are free to receive commands.
        """
        self.stage_port.write(self._format_command_string("STATUS"))

        return self.await_response(response_has_newline=False)

    def await_motors_ready(self) -> None:
        """
        Returns when both motors are ready to receive commands
        """
        while True:
            response = self.check_motor_status()

            if response == "N":
                return


if __name__ == "__main__":
    stage = Controller("COM3")

    # Send check
    check_successful, check_response = stage.send_check("X")

    if check_successful:
        print(check_response)

    # Speed controls
    set_speed_successful, set_speed_response = stage.set_speed({"X": 10000})

    if set_speed_successful:
        print("Successfully set X motor speed!")

    get_speed_successful, get_speed_response = stage.get_speed("X")

    if get_speed_successful:
        print(get_speed_response)

    # Acceleration controls
    set_acceleration_successful, set_acceleration_response = stage.set_acceleration({"Y": 5})

    if set_acceleration_successful:
        print("Successfully set Y motor acceleration!")

    get_acceleration_successful, get_acceleration_response = stage.get_acceleration("Y")

    if get_acceleration_successful:
        print(get_acceleration_response)

    stage.await_motors_ready()
    stage.move_absolute({"X": 0, "Y": 0})
    stage.await_motors_ready()
    print("Done moving")
