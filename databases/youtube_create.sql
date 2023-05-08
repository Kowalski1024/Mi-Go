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
    viedoId INTEGER,
    lang TEXT,
    CONSTRAINT PK_transcript PRIMARY KEY (id, lang),
    FOREIGN KEY (videoId) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS ManuallyCreatedTranscripts (
    videoId INTEGER,
    lang TEXT,
    CONSTRAINT PK_transcript PRIMARY KEY (id, lang),
    FOREIGN KEY (videoId) REFERENCES Video(id)
);

-- TranscriptDifference
CREATE TABLE IF NOT EXISTS TranscriptDiffResults (
    videoId INTEGER PRIMARY KEY,
    wer FLOAT,
    matchRatio FLOAT,
    detectedLanguage TEXT,
    FOREIGN KEY (videoId) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS TranscriptDiffReplace (
    videoId INTEGER,
    model TEXT,
    yt TEXT,
    FOREIGN KEY (videoId) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS TranscriptDiffInsertDelete (
    videoId INTEGER,
    word TEXT,
    operation INTEGER,
    FOREIGN KEY (videoId) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS TranscriptDiffAdditional (
    requestId INTEGER,
    model TEXT,
    FOREIGN KEY (videoId) REFERENCES Request(requestId)
);



