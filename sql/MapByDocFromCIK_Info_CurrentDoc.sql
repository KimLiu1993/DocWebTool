SELECT   mp.DocumentId
        ,mp.ContainerId as FilingId
        ,mp.ProcessId
        ,case mp.DocumentType when 1 then 'Prospectus'
                        when 3 then 'SAI'
                        when 17 then 'Summary Prospectus' end as DocType
            ,mp.EffectiveDate
            ,(select count(im.InvestmentId) from DocumentAcquisition..InvestmentMapping im where im.ProcessId =mp.ProcessId) as [MappingNum]
FROM DocumentAcquisition..MasterProcess as mp
where mp.DocumentId in (%s)