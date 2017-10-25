select distinct im.InvestmentId,count(distinct m.DocumentId) as [DocCount],ss.SecurityName,
   case ss.Status when 0 then 'Obsolete'
                  when 1 then 'Active'
                  when 2 then 'Pending' end as SecIDStatus,
   ss.Universe
from DocumentAcquisition..SECFiling as f
left join DocumentAcquisition..SECFiling as f1 on f1.CIK=f.CIK
left join DocumentAcquisition..MasterProcess as m on m.ContainerId=f1.FilingId
left join DocumentAcquisition..InvestmentMapping as im on im.ProcessId=m.ProcessId
left join SecurityData..SecuritySearch as ss on ss.SecId=im.InvestmentId
where f.FilingId in (%s) 
  and m.DocumentType in (1,2,3,4,5,14) and m.Status<>5
group by im.InvestmentId,ss.SecurityName,ss.Status,ss.Universe
order by count(distinct m.DocumentId) desc