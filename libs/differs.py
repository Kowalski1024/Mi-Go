from difflib import SequenceMatcher

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


def difflib_differ(model_transcript: str, yt_transcript: str) -> dict:
    """
    Basic differ, returns the number of substitutions, insertions, deletions and the wer.
    Uses the SequenceMatcher from difflib

    Args:
        model_transcript: transcript from the model
        yt_transcript: transcript from the target

    Returns:
        dict with the results of the comparison
    """

    results = {"replace": [], "delete": [], "insert": []}

    # split the transcripts into words
    model_set = model_transcript.split()
    yt_set = yt_transcript.split()

    # compare the words
    seq_matcher = SequenceMatcher(a=model_set, b=yt_set, autojunk=False)

    # sort the results into the different categories
    for tag, alo, ahi, blo, bhi in seq_matcher.get_opcodes():
        if tag == "replace":
            results[tag].extend(zip(model_set[alo:ahi], yt_set[blo:bhi]))
        elif tag == "delete":
            results[tag].extend(model_set[alo:ahi])
        elif tag == "insert":
            results[tag].extend(yt_set[blo:bhi])

    # calculate wer
    s = len(results["replace"])
    i = len(results["delete"])
    d = len(results["insert"])

    results["wer"] = (s + i + d) / len(model_set)
    results["matchRatio"] = seq_matcher.ratio()

    return results
