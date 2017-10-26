SELECT distinct cim.InvestmentId
from DocumentAcquisition..FilingSECContract as fsc
left join DocumentAcquisition..ContractIdInvestmentMapping as cim on cim.ContractId=fsc.ContractId
left join SecurityData..SecuritySearch as ss on cim.InvestmentId = ss.SecId
where ss.Status != 0
and fsc.CIK in  (
				SELECT distinct fsc1.CIK
				from DocumentAcquisition..FilingSECContract as fsc1
				where fsc1.FilingId = %s
				)
