import jiwer


def jiwer_differ(model_transcript: str, yt_transcript: str) -> dict:
    """
    Calculate the speach-to-text metrics using the jiwer library

    Args:
        model_transcript: transcript from the model
        yt_transcript: transcript from the target

    Returns:
        dict with the results of the comparison
    """

    results = jiwer.compute_measures(model_transcript, yt_transcript)
    results.pop("ops")
    results.pop("truth")
    results.pop("hypothesis")
    return results
