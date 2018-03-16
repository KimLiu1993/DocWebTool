select ml.ProcessId,ml.DocumentId,sp.Value as [DocType],
        ml.Status,
        ml.EffectiveDate,ml.InvestmentMapping,ml.FileHashcode,
        ac.Email as [User],dateadd(hour,%s,ml.CreationDate) as [Time]
    from DocumentAcquisition..MasterProcessLog as ml
    left join DocumentAcquisition..Account as ac on ac.DaId=ml.UpdateUserId
    left join DocumentAcquisition..SystemParameter as sp on sp.CategoryId=105 and sp.CodeInt=ml.DocumentType
    where ml.ProcessId=%s  and ml.Status in (1,10) 
    order by ml.LogId