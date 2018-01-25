select B.*,
       Mapping_Flag=case when B.CuttingHour+B.MappingHour<=24 then '0-24 BHs'
                          else '>24 BHs' end
From (select A.*,
           CuttingHour=case when [Weekday]='Friday' then datediff(hour,A.MaxFiledate,A.DocCreationDate)-48
                           else datediff(hour,A.MaxFiledate,A.DocCreationDate) end ,
           MappingHour=case when [Weekday]='Friday' then datediff(hour,A.EffectiveDate,A.MappingDate)-48
                           else datediff(hour,A.EffectiveDate,A.MappingDate) end
      From
       (select datepart(year,s.FileDate) as [Year],
               datepart(month,s.FileDate) as [Month],
               d.DocumentId, 
               s.FileDate,
               s.FilingId,
               datename(weekday,s.FileDate) as [Weekday],
               dateadd(hour,14,s.CreationDate) as FilingDownloadDate,
               dateadd(hour,14,d.CreationDate) as DocCreationDate,
               --d.EffectiveDate,
               --MappingDate=case when d.UpdateDate is null then dateadd(hour,14,d.CreationDate) else dateadd(hour,14,d.UpdateDate) end,
			   MappingDate=(
							 select top 1 MM.CreationDate from DocumentAcquisition..MasterProcessLog as MM
							 where MM.DocumentId=d.DocumentId and MM.InvestmentMapping is not null
							 order by MM.LogId
							   ),
               EffectiveDate=case when s.CreationDate>d.EffectiveDate then dateadd(hour,14,s.CreationDate) else dateadd(hour,14,d.EffectiveDate) end,
               MaxFiledate=case when s.FileDate> s.CreationDate then dateadd(hour,24,s.FileDate) else dateadd(hour,14,s.CreationDate)end
         FROM DocumentAcquisition..MasterProcess d 
         join DocumentAcquisition..SECFiling s on s.FilingId=d.ContainerId
         --left join LogData..DocumentOperationTracking dm on dm.DocumentId=d.DocumentId and (DataPoint='Status' and PreviousValue=0)
         where d.Category=5 and s.FilingId>0 and d.Status<>3 and d.DocumentDate>='2016-11-30' and d.Status<>5 ) as A
) AS B
