select fc.ContractId,fc.SeriesName,fc.ContractName,fc.CIK,fc.FilingId,fc.Accession,f.FormType,f.FileDate
from DocumentAcquisition..FilingSECContract as fc
left join DocumentAcquisition..SECFiling as f on f.FilingId=fc.FilingId
where fc.ContractId='%s'
order by fc.ContractId,f.FileDate desc