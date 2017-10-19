select top 1 ac.Email as [Cutter],dateadd(hour,%s,m.CreationDate) as [Cutting Time(SZ)]
from DocumentAcquisition..MasterProcess as m
left join DocumentAcquisition..Account as ac on ac.DaId=m.DA2
where m.ProcessId=%s
