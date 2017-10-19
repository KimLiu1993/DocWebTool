select top 1 ac.Email as [First Mapper],dateadd(hour,%s,mpl.CreationDate) as [Mapping Time(SZ)]
from DocumentAcquisition..MasterProcessLog as mpl
left join DocumentAcquisition..Account as ac on ac.DaId=mpl.UpdateUserId
where mpl.InvestmentMapping is not null and mpl.ProcessId=%s
order by mpl.LogId