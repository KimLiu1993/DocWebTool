select distinct
	   fb.LegalName
from DocumentAcquisition..MasterProcess as mp
left join DocumentAcquisition..InvestmentMapping as im on mp.ProcessId = im.ProcessId
left join CurrentData..FundClassBasic as fcb on im.InvestmentId = fcb.SecId
left join CurrentData..FundBasic as fb on fcb.FundId = fb.FundId
where DocumentId = '%s'
and fb.LegalName is not null