CREATE TABLE IF NOT EXISTS UITTimeliness (
    [Year]                INTEGER,
	[Month]               INTEGER,
	DocumentId            INTEGER  PRIMARY KEY
                                   UNIQUE
                                   NOT NULL,
    FileDate              DATETIME,
    FilingId              INTEGER,
    [Weekday]             TEXT,
    FilingDownloadDate    DATETIME,
	DocCreationDate       DATETIME,
	MappingDate           DATETIME,
	EffectiveDate         DATETIME,
	MaxFiledate           DATETIME,
	CuttingHour,
	MappingHour,
	Mapping_Flag          TEXT
);
