CREATE TABLE IF NOT EXISTS VATimeliness (
    ProcessId             INTEGER  PRIMARY KEY
                                   UNIQUE
                                   NOT NULL,
    DocumentType               TEXT     NOT NULL,
    [FixedDocumentDateSZ] DATETIME,
    FixedCreationDateSZ   DATETIME,
    FixedMappingDateSZ    DATETIME,
	FixedAtivationDateSZ  DATETIME,
	CutTime,
	MapTime,
	[Total],
	[Time_Flag]           TEXT,
	[Document_Flag]       TEXT,
	[Result]              TEXT
);
