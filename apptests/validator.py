import argparse

from youtube_transcript_api import YouTubeTranscriptApi

import models


class ModelClassValidator:
    def __init__(self, class_name, language, model_type):
        module_attrs = vars(models)
        model_class = module_attrs.get(class_name)
        self.model_instance = model_class()
        self.language = language
        self.model_type = model_type

    def get_yt_transcript(self, video_id: str) -> str:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        srt = transcripts.find_generated_transcript(language_codes=["en"]).fetch()

        return " ".join(fragment["text"] for fragment in srt)

    def check_attributes(self) -> dict:
        expected_attributes = ["model", "transcriber", "differ"]
        check_results_dict = {}
        for e in expected_attributes:
            if not hasattr(self.model_instance, e):
                check_results_dict[e + "_field"] = "you must provide " + e + " field"

        target_transcript = self.get_yt_transcript("QkkoHAzjnUs")
        check_results_dict["target_transcript"] = target_transcript

        try:
            returned_transcript = self.model_instance.transcribe("apptests/sample.mp3")

            if type(returned_transcript) is not str:
                check_results_dict[
                    "transcribe_method"
                ] = "transcribe method must return str"

            check_results_dict["model_transciption"] = returned_transcript
        except Exception as e:
            check_results_dict["transcribe_method"] = type(e).__name__ + " occured"

        try:
            differ_results = self.model_instance.compare(
                returned_transcript, target_transcript
            )

            if type(differ_results) is not dict:
                check_results_dict["compare_method"] = "compare method must return dict"

            check_results_dict["comparison_results"] = returned_transcript
        except Exception as e:
            check_results_dict["compare_method"] = type(e).__name__ + " occured"

        return check_results_dict

    def log_errors(self, errors_dict):
        if errors_dict:
            for key, value in errors_dict.items():
                print(key + ":  " + value)
        else:
            print("Model class is ready to use")

    def validate(self):
        results = self.check_attributes()
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
    mc = ModelClassValidator(
        args["class_name"], args["relevance_language"], args["model_type"]
    )
    mc.validate()


if __name__ == "__main__":
    main()
