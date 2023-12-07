import argparse
import models

from src.dataclasses import YouTubeVideo

class ModelClassValidator:
    def __init__(self, class_name): 
        module_attrs = vars(models)
        model_class = module_attrs.get(class_name)
        self.model = model_class()

        
        

    def validate(self):
        returned_transcript = self.model.transcribe("apptests/sample.mp3")

        # title: str
        # videoId: str
        # defaultAudioLanguage: str
        # generatedTranscripts: list
        # manuallyCreatedTranscripts: list
        
        
        video = YouTubeVideo.from_dict({"title": "gtaV", "videoId": "QkkoHAzjnUs", "defaultAudioLanguage": "en", "generatedTranscripts": ["en"], "manuallyCreatedTranscripts": ["en"]})
          
        target_transcript = video.youtube_transcript("en")

        self.model_class.compare(returned_transcript, target_transcript)



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
        "--relevanceLanguage",
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
    mc = ModelClassValidator(args["class_name"])
    mc.validate()


if __name__ == "__main__":
    main()
    