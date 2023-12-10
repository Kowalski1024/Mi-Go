import argparse

from youtube_transcript_api import YouTubeTranscriptApi

import models
from src.transcript_test import TranscriptTest


class ModelClassValidator:
    def __init__(self, model, language, model_type):
        try:
            if not isinstance(model, TranscriptTest):
                raise TypeError("model must be instance of TranscriptTest class")
            self.model_instance = model
        except Exception as e:
            print(type(e).__name__ + " occured: " + str(e))
            exit(1)
        
        self.language = language
        self.model_type = model_type

    def get_yt_transcript(self) -> str:
        with open('data/transcript.txt', 'r') as file:
            content = file.read()
            return content
        
    def check_attributes(self, check_results) -> dict:
        expected_attributes = ["model", "transcriber", "differ"]
        for e in expected_attributes:
            if not hasattr(self.model_instance, e):
                check_results[e + "_field"] = "you must provide " + e + " field"

    def run_transcribe(self, check_results) -> str:
        target_transcript = self.get_yt_transcript()
        check_results["target_transcript"] = target_transcript

        try:
            returned_transcript = self.model_instance.transcribe("apptests/data/sample.mp3")

            if type(returned_transcript) is not str:
                check_results[
                    "transcribe_method"
                ] = "transcribe method must return str"

            check_results["model_transciption"] = returned_transcript
        except Exception as e:
            check_results["transcribe_method"] = type(e).__name__ + " occured"

    def run_compare(self, check_results) -> dict:
        try:
            differ_results = self.model_instance.compare(
                check_results["model_transciption"] , check_results["target_transcript"]
            )

            if type(differ_results) is not dict:
                check_results["compare_method"] = "compare method must return dict"

            check_results["comparison_results"] = differ_results
        except Exception as e:
            check_results["compare_method"] = type(e).__name__ + " occured"

    def run_additional_info(self, check_results) -> dict:
        try:
            additional_info = self.model_instance.additional_info()

            if type(additional_info) is not dict:
                check_results["additional_info_method"] = "additional_info method must return dict"

            check_results["additional_info"] = additional_info
        except Exception as e:
            check_results["additional_info_method"] = type(e).__name__ + " occured"

    def check_model(self) -> dict:
        check_results_dict = {}
        self.check_attributes(check_results_dict)
        self.run_transcribe(check_results_dict)
        self.run_compare(check_results_dict)
        self.run_additional_info(check_results_dict)
        return check_results_dict

    def log_errors(self, errors_dict):
        if errors_dict:
            for key, value in errors_dict.items():
                if type(value) is dict:
                    print(key + ":")
                    for k, v in value.items():
                        print("    " + k + ":  " + v)
                else:
                    print(key + ":  " + value)
        else:
            print("Model class is ready to use")

    def validate(self):
        results = self.check_model()
        self.log_errors(results)


def command_parser() -> argparse.Namespace:
    """
    Parse command line arguments

    Returns:
        parsed arguments
    """

    parser = argparse.ArgumentParser(
        prog="Models class validator",
        description="Test if user model class is ready to use",
    )
    parser.add_argument("-c", "--class-name", type=str, required=True)
    parser.add_argument(
        "-l",
        "--relevance-language",
        required=False,
        type=str,
        default="en",
    )
    parser.add_argument(
        "-m",
        "--model-type",
        type=str,
        required=True,
    )

    return parser.parse_args()


def main():
    args = vars(command_parser())
    module_attrs = vars(models)
    model_class = module_attrs.get(args["class_name"])
    model = model_class()
    mc = ModelClassValidator(
        model, args["relevance_language"], args["model_type"]
    )
    mc.validate()


if __name__ == "__main__":
    main()
