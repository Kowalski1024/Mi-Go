import json
import os
import subprocess
import time
import unittest


class TestYoutubeGenerator(unittest.TestCase):
    def test_directory_and_file_creation(self):
        command = (
            "python3 generators/youtube_generator.py 10 -o ./testplans -c 19 -l en"
        )
        subprocess.run(command, shell=True)

        target_directory = "./testplans"
        self.assertTrue(
            os.path.exists(target_directory), f"{target_directory} does not exist."
        )
        time_str = time.strftime("%Y%m%d-%H%M%S")

        filename = f"Travel&Events_en_CAUQAQ_{time_str}.json"

        json_file_path = os.path.join(target_directory, filename)
        self.assertTrue(
            os.path.exists(json_file_path), f"{json_file_path} does not exist."
        )

        with open(json_file_path, "r") as json_file:
            try:
                json.load(json_file)
            except json.JSONDecodeError:
                self.fail(f"{json_file_path} is not a valid JSON file.")

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
        command = (
            "python3 generators/youtube_generator.py 10 -o ./testplans -c 19 -l en"
        )
        subprocess.run(command, shell=True)
        time_str = time.strftime("%Y%m%d-%H%M%S")
        filename = f"Travel&Events_en_CAUQAQ_{time_str}.json"

        command = (
            f"python3 youtube_runner.py './testplans/{filename}' -st DummyTest -m tiny"
        )
        subprocess.run(command, shell=True)

        filename = f"YouTubeTestRunner_Travel&Events_{time_str}.json"
        output_directory = "./output"
        output_path = os.path.join(output_directory, filename)
        self.assertTrue(
            os.path.exists(output_path), f"Output file {output_path} not found."
        )

        with open(output_path, "r") as output_file:
            output_data = json.load(output_file)

        self.assertEqual(output_data["errors"], 0, "Unexpected errors in the test run.")
        self.assertEqual(output_data["failures"], 1, "Expected test failure not found.")
        self.assertEqual(output_data["testsRun"], 2, "Unexpected number of tests run.")

    def test_testplan_execute_proper_model(self):
        command = (
            "python3 generators/youtube_generator.py 10 -o ./testplans -c 19 -l en"
        )
        subprocess.run(command, shell=True)
        time_str = time.strftime("%Y%m%d-%H%M%S")
        filename = f"Travel&Events_en_CAUQAQ_{time_str}.json"

        command = f"python3 youtube_runner.py './testplans/{filename}' -st WhisperTest -m tiny"
        subprocess.run(command, shell=True)

        filename = f"YouTubeTestRunner_Travel&Events_{time_str}.json"
        output_directory = "./output"
        output_path = os.path.join(output_directory, filename)
        self.assertTrue(
            os.path.exists(output_path), f"Output file {output_path} not found."
        )

        with open(output_path, "r") as output_file:
            output_data = json.load(output_file)

        self.assertEqual(output_data["errors"], 0, "Unexpected errors in the test run.")
        self.assertEqual(output_data["failures"], 1, "Expected test failure not found.")
        self.assertEqual(output_data["testsRun"], 2, "Unexpected number of tests run.")

    def test_execute_with_missing_parameter(self):
        command = (
            "python3 generators/youtube_generator.py 10 -o ./testplans -c 19 -l en"
        )
        subprocess.run(command, shell=True)
        time_str = time.strftime("%Y%m%d-%H%M%S")
        filename = f"Travel&Events_en_CAUQAQ_{time_str}.json"

        command = f"python3 youtube_runner.py ./testplans/{filename}"
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        expected_error_message = b"the following arguments are required"
        self.assertIn(
            expected_error_message,
            result.stderr,
            f"Expected error message not found in stderr.\nActual stderr: {result.stderr.decode()}",
        )
