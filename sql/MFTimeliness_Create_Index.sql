CREATE INDEX IF NOT EXISTS Index_A ON MFTimeliness (
    ProcessId,
    DocType,
    CutTime,
    [Chart/MapTime],
    LinkTime,
    [Total]
);
