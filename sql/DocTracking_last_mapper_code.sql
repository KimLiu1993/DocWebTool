select top 1 ac.Email as [Last Mapper],dateadd(hour,%s,im.UpdateDate) as [Mapping Time(SZ)]
from DocumentAcquisition..InvestmentMapping as im
left join DocumentAcquisition..Account as ac on ac.DaId=im.UpdateUserId
where im.ProcessId=%s
order by im.UpdateDate desc