SELECT  mp.DocumentId
FROM [DocumentAcquisition].[dbo].[InvestmentMapping] as im
left join DocumentAcquisition..MasterProcess as mp on im.ProcessId = mp.ProcessId
where im.InvestmentId = '%s'
and mp.DocumentType = %s
