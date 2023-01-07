from difflib import SequenceMatcher


def differ(model_transcript: str, yt_transcript: str):
    results = {'replace': [], 'delete': [], 'insert': []}

    model_set = model_transcript.split()
    yt_set = yt_transcript.split()

    seq_matcher = SequenceMatcher(a=model_set, b=yt_set, autojunk=False)

    for tag, alo, ahi, blo, bhi in seq_matcher.get_opcodes():
        if tag == 'replace':
            results[tag].extend(zip(model_set[alo:ahi], yt_set[blo:bhi]))
        elif tag == 'delete':
            results[tag].extend(model_set[alo:ahi])
        elif tag == 'insert':
            results[tag].extend(yt_set[blo:bhi])

    s = len(results['replace'])
    i = len(results['delete'])
    d = len(results['insert'])

    results['WER'] = (s+i+d)/len(model_set)
    results['matchRatio'] = seq_matcher.ratio()

    return results
