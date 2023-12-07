import argparse
import models

from src.dataclasses import YouTubeVideo
from youtube_transcript_api import YouTubeTranscriptApi

class ModelClassValidator:
    def __init__(self, class_name, language, model_type): 
        module_attrs = vars(models)
        model_class = module_attrs.get(class_name)
        self.model_instance = model_class()
        self.language = language
        self.model_type = model_type

    def get_yt_transcript(self, video_id: str) -> str:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    
        srt = transcripts.find_generated_transcript(
            language_codes=["en"]
        ).fetch()

        return " ".join(fragment["text"] for fragment in srt)


    def validate(self):
        if not hasattr(self.model_instance, 'model'):
            print("you must provide model")
        if not hasattr(self.model_instance, 'transcriber'):
            print("you must provide transcriber")
        if not hasattr(self.model_instance, 'differ'):
            print("you must provide differ")
            
        try:
            returned_transcript = self.model_instance.transcribe("apptests/sample.mp3")
            
        except NotImplementedError as e:
            print("you must provide transcribe method")
            return
        
        target_transcript = self.get_yt_transcript("QkkoHAzjnUs")
        try:
            self.model_instance.compare(returned_transcript, target_transcript) 
        except Exception as e:
            print("you must provide compare method")
            print(type(e).__name__)
            return


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
    parser.add_argument(
        "-c", "--class-name", type=str, required=True
    )
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
    mc = ModelClassValidator(args["class_name"], args["relevance_language"], args["model_type"])
    mc.validate()


if __name__ == "__main__":
    main()
    