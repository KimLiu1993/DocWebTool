select distinct ci.InvestmentId
from DocumentAcquisition..FilingSECContract as fc 
left join DocumentAcquisition..ContractIdInvestmentMapping as ci on fc.ContractId = ci.ContractId
left join SecurityData..SecuritySearch as ss on ci.InvestmentId = ss.SecId
where fc.CIK in (%s)
and ss.Status != 0