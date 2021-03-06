import unittest
from time import sleep

import numpy
from bsread.sender import sender
from multiprocessing import Process, Event
from bsread import source, PULL, json
from scipy import ndimage

from psss_processing import config
from psss_processing.processor import get_stream_processor, process_image


class TestProcessing(unittest.TestCase):

    def test_process_image(self):
        image = numpy.zeros(shape=(1024, 512), dtype="uint16")
        image += 1

        pv_name_prefix = "JUST_TESTING"

        axis = numpy.linspace(9100, 9200, 512)

        roi = [0, 1024]
        parameters = {"background": ""}

        processed_data = process_image(image, axis, pv_name_prefix, roi, parameters)
        self.assertSetEqual(set(processed_data.keys()), {pv_name_prefix + ":processing_parameters",
                                                         pv_name_prefix + ":SPECTRUM_Y",
                                                         pv_name_prefix + ":SPECTRUM_X",
                                                         pv_name_prefix + ":SPECTRUM_CENTER",
                                                         pv_name_prefix + ":SPECTRUM_FWHM",
                                                         pv_name_prefix + config.EPICS_PV_SUFFIX_IMAGE})

        # Original image should not be manipulated
        self.assertEqual(image.shape, (1024, 512))

        self.assertEqual(len(processed_data[pv_name_prefix + ":SPECTRUM_Y"]), 512)

        processing_parameters = json.loads(processed_data[pv_name_prefix + ":processing_parameters"])

    def test_stream_processor(self):
        pv_name_prefix = "JUST_TESTING"
        n_images = 50
        original_parameters = {"background": ""}

        image = numpy.zeros(shape=(1024, 512), dtype="uint16")
        image += 1

        data_to_send = {pv_name_prefix + config.EPICS_PV_SUFFIX_IMAGE: image}

        def send_data():
            with sender(port=10000, queue_size=100) as output_stream:
                for x in range(n_images):
                    output_stream.send(data=data_to_send)

        def process_data(event):
            stream_processor = get_stream_processor(input_stream_host="localhost",
                                                    input_stream_port=10000,
                                                    data_output_stream_port=11000,
                                                    image_output_stream_port=11001,
                                                    epics_pv_name_prefix=pv_name_prefix,
                                                    output_pv_name="Does not matter",
                                                    center_pv_name="",
                                                    fwhm_pv_name="",
                                                    ymin_pv_name="",
                                                    ymax_pv_name="",
                                                    axis_pv_name="")

            stream_processor(event, original_parameters, {})

        running_event = Event()

        send_process = Process(target=send_data)
        processing_process = Process(target=process_data, args=(running_event,))

        send_process.start()
        sleep(1)
        processing_process.start()

        final_data = []

        with source(host="localhost", port=11000, mode=PULL) as input_stream:
            final_data.append(input_stream.receive())

        running_event.clear()

        sleep(0.2)

        send_process.terminate()
        processing_process.terminate()

        self.assertEqual(len(final_data), 1)

        parameters = final_data[0].data.data[pv_name_prefix + ":processing_parameters"].value
        processing_parameters = json.loads(parameters)

        spectrum = final_data[0].data.data[pv_name_prefix + ":SPECTRUM_Y"].value

        self.assertEqual(len(spectrum), 512)
        self.assertListEqual(list(spectrum), [1024] * 512)
