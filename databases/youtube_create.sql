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
CREATE TABLE IF NOT EXISTS TranscriptDiffAdditional (
    requestId INTEGER,
    model TEXT,
    language TEXT DEFAULT NULL,
    werMean FLOAT,
    werStd FLOAT,
    FOREIGN KEY (requestId) REFERENCES Request(requestId)
);

-- DiffLib
CREATE TABLE IF NOT EXISTS DiffLibResults (
    id INTEGER PRIMARY KEY,
    wer FLOAT,
    matchRatio FLOAT,
    detectedLanguage TEXT,
    FOREIGN KEY (id) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS DiffLibReplace (
    id INTEGER,
    model TEXT,
    yt TEXT,
    FOREIGN KEY (id) REFERENCES Video(id)
);

CREATE TABLE IF NOT EXISTS DiffLibInsertDelete (
    id INTEGER,
    word TEXT,
    operation INTEGER,
    FOREIGN KEY (id) REFERENCES Video(id)
);

-- JiWER
CREATE TABLE IF NOT EXISTS JiWERResults (
    id INTEGER PRIMARY KEY,
    wer FLOAT,
    mer FLOAT,
    wil FLOAT,
    wip FLOAT,
    hits INTEGER,
    substitutions INTEGER,
    deletions INTEGER,
    insertions INTEGER,
    detectedLanguage TEXT,
    FOREIGN KEY (id) REFERENCES Video(id)
);



