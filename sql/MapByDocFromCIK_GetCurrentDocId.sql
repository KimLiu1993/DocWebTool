SELECT DocumentId
FROM [DocumentAcquisition].[dbo].[SECCurrentDocument]
where InvestmentId = '%s'
and DocumentType = '%s'