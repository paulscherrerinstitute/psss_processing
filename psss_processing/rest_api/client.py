import requests

from psss_processing import config


def validate_response(server_response):
    if server_response["state"] != "ok":
        raise ValueError(server_response.get("status", "Unknown error occurred."))

    return server_response


class PsssProcessingClient(object):
    def __init__(self, address="http://sf-daqsync-02:12000/"):
        """
        :param address: Address of the PSSS Processing service, e.g. http://localhost:12000
        """

        self.api_address_format = address.rstrip("/") + config.API_PREFIX + "%s"
        self.address = address

    def get_address(self):
        """
        Return the REST api endpoint address.
        """
        return self.address

    def start(self):
        """
        Start the processing.

        :return: Server status.
        """
        rest_endpoint = "/start"

        server_response = requests.post(self.api_address_format % rest_endpoint).json()
        return validate_response(server_response)["status"]

    def stop(self):
        """
        Stop the processing.

        :return: Server status.
        """
        rest_endpoint = "/stop"

        server_response = requests.post(self.api_address_format % rest_endpoint).json()
        return validate_response(server_response)["status"]

    def get_status(self):
        """
        Get the status of the processing.

        :return: Server status.
        """
        rest_endpoint = "/status"

        server_response = requests.get(self.api_address_format % rest_endpoint).json()
        return validate_response(server_response)["status"]

    def get_statistics(self):
        """
        Get the statistics of the processing.

        :return: Server statistics.
        """
        rest_endpoint = "/statistics"

        server_response = requests.get(self.api_address_format % rest_endpoint).json()
        return validate_response(server_response)["statistics"]

    def get_parameters(self):
        """
        Get the processing parameters

        :return: Processing parameters as a dictionary.
        """
        rest_endpoint = "/parameters"

        server_response = requests.get(self.api_address_format % rest_endpoint).json()
        return validate_response(server_response)["parameters"]

    def set_parameters(self, parameters):
        """
        Set the processing parameters

        :param parameters: Dictionary with 3 elements: min_threshold, max_threshold, rotation
        :return: Set parameters.
        """
        rest_endpoint = "/parameters"

        server_response = requests.post(self.api_address_format % rest_endpoint, json=parameters).json()
        return validate_response(server_response)["parameters"]

    def set_background(self, filename='', data=None):
        """
        Set the background image. If no arguments are provided, the background image is cleared.

        :param str filename: background image filename. It is used merely to track where 
                             the background image is loaded.
        :param ndarray data: background image data.
        """
        rest_endpoint = "/background"

        if data is not None:
            data = data.tolist()

        parameters = {
            "filename": filename,
            "data": data
        }
        server_response = requests.post(self.api_address_format % rest_endpoint, json=parameters).json()
        return validate_response(server_response)["state"]
