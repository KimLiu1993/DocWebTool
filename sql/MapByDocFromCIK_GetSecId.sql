﻿select distinct ci.InvestmentId
from DocumentAcquisition..FilingSECContract as fc 
left join DocumentAcquisition..ContractIdInvestmentMapping as ci on fc.ContractId = ci.ContractId
where fc.FilingId = %s