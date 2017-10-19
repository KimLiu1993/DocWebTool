select top 1 ac.Email as [Chart User],dateadd(hour,%s,dct.LastUpdate) as [Chart Time]
from DocumentAcquisition..DocumentChartTracking as dct
left join DocumentAcquisition..Account as ac on ac.DaId=dct.UserId
where dct.NeedChart=1 and dct.AddChart=1 and dct.DocumentId=%s
order by dct.TrackingId desc