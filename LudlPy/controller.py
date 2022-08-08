# Jayden Roberts
# 8/8/22

import serial

default_communication_parameters = {
    "baudrate": 19200,
    "bytesize": serial.EIGHTBITS,
    "parity": serial.PARITY_NONE,
    "stopbits": serial.STOPBITS_TWO,
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
            port=serial_port_name, **default_communication_parameters
        )

        return port_connection

    @staticmethod
    def _format_command_string(command: str) -> bytes:
        """
        This function is used to convert the input command into a readable format for the controller.
        This is accomplished by adding a carriage return to the end of the command string,
        and converting the string to binary using the ASCII standard.

        :param command: The command string to be written to the buffer.
        :return: Returns the response from the controller in ASCII formatting.
        """
        carriage_command = f"{command}\r"
        return carriage_command.encode("ASCII")

    def await_response(self) -> str:
        """
        Return the response from some command.

        :return: The response from the controller.
        """
        while True:
            if self.stage_port.in_waiting > 0:
                return self.stage_port.readline().decode("ASCII")

    def send_check(self, motor_id: str = "X") -> str:
        """
        Ensure the connection to the controller has been established successfully.

        :param motor_id: Which stage dimension to use. Currently, "X" & "Y" are supported.
        :return: The response from the controller.
        """
        self.stage_port.write(self._format_command_string(f"RDSTAT {motor_id}"))

        return self.await_response()


if __name__ == "__main__":
    stage = Controller("COM3")

    response = stage.send_check("X")
    print(response)
