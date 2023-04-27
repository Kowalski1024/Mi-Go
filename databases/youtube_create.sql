-- TESTPLAN BASE

CREATE TABLE IF NOT EXISTS Request (
    requestId INTEGER PRIMARY KEY AUTOINCREMENT,
    nextPageToken TEXT NULL,
    regionCode TEXT,
    videoCategoryId TEXT,
    etag TEXT
);

CREATE TABLE IF NOT EXISTS Args (
    requestId INTEGER PRIMARY KEY,
    maxResults INTEGER,
    pageToken TEXT NULL,
    q TEXT NULL,
    videoCategoryId TEXT NULL,
    regionCode TEXT NULL,
    relevanceLanguage TEXT NULL,
    topicId TEXT NULL,
    videoDuration TEXT NULL,
    FOREIGN KEY (requestId) REFERENCES Request(requestId)
);

CREATE TABLE IF NOT EXISTS Video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requestId INTEGER,
    videoId TEXT,
    defaultAudioLanguage TEXT NULL,
    duration TEXT,
    FOREIGN KEY (requestId) REFERENCES request(requestId),
    CONSTRAINT UC_video UNIQUE (videoId, requestId)
);

CREATE TABLE IF NOT EXISTS GeneratedTranscripts (
    id INTEGER,
    lang TEXT,
    CONSTRAINT PK_transcript PRIMARY KEY (id, lang),
    FOREIGN KEY (id) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS ManuallyCreatedTranscripts (
    id INTEGER,
    lang TEXT,
    CONSTRAINT PK_transcript PRIMARY KEY (id, lang),
    FOREIGN KEY (id) REFERENCES Video(id)
);

-- TranscriptDifference
CREATE TABLE IF NOT EXISTS TranscriptDiffResults (
    id INTEGER PRIMARY KEY,
    wer FLOAT,
    matchRatio FLOAT,
    detectedLanguage TEXT,
    FOREIGN KEY (id) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS TranscriptDiffReplace (
    id INTEGER,
    model TEXT,
    yt TEXT,
    FOREIGN KEY (id) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS TranscriptDiffInsertDelete (
    id INTEGER,
    word TEXT,
    operation INTEGER,
    FOREIGN KEY (id) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS TranscriptDiffAdditional (
    id INTEGER,
    model TEXT,
    FOREIGN KEY (id) REFERENCES Request(requestId)
);



