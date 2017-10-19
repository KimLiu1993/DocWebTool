select ac.Email as [Link User],dateadd(hour,%s,link.LinkLastUpdate) as [Link Time]
from DocumentAcquisition..DocumentDataNode as link
left join DocumentAcquisition..Account as ac on ac.DaId=link.AddAnchorUser
where link.ProcessId=%s