CREATE INDEX IF NOT EXISTS Index_B ON VATimeliness (
    ProcessId,
    DocumentType,
    CutTime,
    [MapTime],
    [Total]
);
