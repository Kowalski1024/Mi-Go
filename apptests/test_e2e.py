import json
import os
import shutil
import subprocess
import time
import unittest


class TestYoutubeGenerator(unittest.TestCase):
    def setUp(self):
        self.path = "apptests/data/simpleTest.json"
        self.generate_dir = "apptests/testplans"

    def test_directory_and_file_creation(self):
        command = f"python3 generators/youtube_generator.py 10 -o {self.generate_dir} -c 19 -l en"

        subprocess.run(command, shell=True)

        self.assertTrue(
            os.path.exists(self.generate_dir), f"{self.generate_dir} does not exist."
        )
        time_str = time.strftime("%Y%m%d-%H%M%S")

        filename = f"Travel&Events_en_CAUQAQ_{time_str}.json"

        json_file_path = os.path.join(self.generate_dir, filename)
        self.assertTrue(
            os.path.exists(json_file_path), f"{json_file_path} does not exist."
        )

        with open(json_file_path, "r") as json_file:
            try:
                json.load(json_file)
            except json.JSONDecodeError:
                self.fail(f"{json_file_path} is not a valid JSON file.")

        shutil.rmtree(self.generate_dir)

    def test_missing_required_parameter(self):
        command = "python3 generators/youtube_generator.py -o ./testplans -c 19 -l en"
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        expected_error_message = "the following arguments are required: maxResults"
        self.assertIn(
            expected_error_message,
            result.stderr.decode(),
            f"Expected error message not found in stderr.\nActual stderr: {result.stderr.decode()}",
        )

    def test_testplan_execute_test_model(self):
        command = f"python3 youtube_runner.py {self.path} -st DummyTest -m tiny"
        subprocess.run(command, shell=True)
        time_str = time.strftime("%Y%m%d-%H%M%S")

        filename = f"Travel & Events_YouTubeTestRunner_{time_str}.json"
        output_directory = "./output"
        output_path = os.path.join(output_directory, filename)
        self.assertTrue(
            os.path.exists(output_path), f"Output file {output_path} not found."
        )

        with open(output_path, "r") as output_file:
            output_data = json.load(output_file)

        self.assertEqual(output_data["args"]["q"], "Travel & Events")

    def test_testplan_execute_proper_model(self):
        command = f"python3 youtube_runner.py {self.path} -st WhisperTest -m tiny"
        subprocess.run(command, shell=True)
        time_str = time.strftime("%Y%m%d-%H%M%S")

        filename = f"Travel & Events_YouTubeTestRunner_{time_str}.json"
        output_directory = "./output"
        output_path = os.path.join(output_directory, filename)
        self.assertTrue(
            os.path.exists(output_path), f"Output file {output_path} not found."
        )

        with open(output_path, "r") as output_file:
            output_data = json.load(output_file)

        self.assertEqual(output_data["args"]["q"], "Travel & Events")

    def test_execute_with_missing_parameter(self):
        command = f"python3 youtube_runner.py {self.path} -st WhisperTest -m tiny"
        subprocess.run(command, shell=True)
        time_str = time.strftime("%Y%m%d-%H%M%S")

        command = f"python3 youtube_runner.py {self.path}"
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        expected_error_message = b"the following arguments are required"
        self.assertIn(
            expected_error_message,
            result.stderr,
            f"Expected error message not found in stderr.\nActual stderr: {result.stderr.decode()}",
        )
