CREATE TABLE IF NOT EXISTS pairs (
    code TEXT PRIMARY KEY
);

-- Labels (category) live only here; clip files and URLs use random ids.
CREATE TABLE IF NOT EXISTS clips (
    id TEXT PRIMARY KEY,
    pair_code TEXT NOT NULL REFERENCES pairs(code),
    speaker TEXT NOT NULL CHECK (speaker IN ('A', 'B')),
    category TEXT NOT NULL CHECK (category IN ('echt', '3s', '6s', '10s')),
    created REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id TEXT NOT NULL REFERENCES clips(id),
    rater_code TEXT NOT NULL,
    rater_id TEXT NOT NULL,
    answer TEXT NOT NULL CHECK (answer IN ('echt', 'nep')),
    correct INTEGER NOT NULL,
    created REAL NOT NULL,
    UNIQUE (clip_id, rater_id)
);

CREATE INDEX IF NOT EXISTS ratings_rater ON ratings(rater_id);
CREATE INDEX IF NOT EXISTS ratings_clip ON ratings(clip_id);
CREATE INDEX IF NOT EXISTS clips_pair ON clips(pair_code);
