
------------------------------------
--Author:        Violet Cai
--CreationDate:  2017-10-30
--RevisedDate:   
------------------------------------

select Z.ProcessId,Z.DocumentType,Z.FixedDocumentDateSZ   
			 ,Z.FixedCreationDateSZ
			 ,Z.FixedMappingDateSZ
			 ,min(Z.FixedAtivationDateSZ) as [FixedAtivationDateSZ]
			 ,Z.CutTime
       		 ,Z.MapTime
			 ,Z.Total
			 ,Z.Time_Flag
			 ,Z.Document_Flag
			 ,Z.Result
from(
	select  distinct A.ProcessId
			 ,A.DocumentType	
			 ,A.FixedDocumentDateSZ   
			 ,A.FixedCreationDateSZ
			 ,A.FixedMappingDateSZ
			 ,A.FixedAtivationDateSZ
			 ,A.CutTime
       		 ,A.MapTime
       		 ,Total= A.CutTime+A.MapTime
       		 ,(case when A.CutTime+A.MapTime<=900 then '<=15BHr'
       		   else '>15BHr' end ) as 'Time_Flag'
       		 ,A.Document_Flag
       		 ,(case when A.CutTime+A.MapTime<=900 OR A.Document_Flag='Historical'then 'Free'
       				  else  'Defect' end ) as 'Result'
       	
	   from(  
			 select
				   B.ProcessId
				  ,B.DocumentType	
				  ,B.FixedDocumentDateSZ 
				  ,B.FixedCreationDateSZ
				  ,B.FixedMappingDateSZ
				  ,B.FixedAtivationDateSZ
				  ,datediff(MINUTE,B.FixedDocumentDateSZ,B.FixedCreationDateSZ) as 'CutTime'--doc被切出来的时间减doc进来需要被处理的时间
				  ,datediff(MINUTE,B.FixedCreationDateSZ,B.FixedMappingDateSZ) as 'MapTime'--doc做上mapping的时间减doc被切出来的时间
				  ,Document_Flag=case when B.FixedAtivationDateSZ>B.FixedDocumentDateSZ then 'Historical'
								  else 'Daily' end --contractID被激活的时间大于doc被切出来的时间，policy update产生的doc为Historical，否则为daily产生的doc

			from( 
				  select  C.ProcessId
						 ,C.DocumentType	               
						 ,C.DocumentDate
						 ,case when datepart(weekday,C.DocumentDate)=6 then dateadd(day,2,DATEADD(hour,33,C.DocumentDate))
		   				  else DATEADD(hour,33,C.DocumentDate) end as 'FixedDocumentDateSZ'
		   				  --美国第一天日期的filing在深圳日期第二天被处理，所以统一加上24小时日期 然后加上上班时间9点，所以加上33小时
		   				  --考虑了美国周五的Filing在深圳周一时间才会被处理，所以加上加了3天
                    
						 ,C.CreationDate
		   				 ,case when datepart(weekday,C.CreationDate)=6 and DATEPART(hour,DATEADD(hour,13,C.CreationDate))>=18 then dateadd(day,2,DATEADD(hour,13,C.CreationDate))
		   				  else DATEADD(hour,13,C.CreationDate) end as 'FixedCreationDateSZ'
		   				  --doc被切出来的深圳时间（13小时差）
		   				  --美国日期周五并且深圳时间周五18点之后切出来的doc加上两天
	         
						,C.MappingDate
						,case when datepart(weekday,C.MappingDate)=6 and DATEPART(hour,DATEADD(hour,13,C.MappingDate))>=18 then dateadd(day,2,DATEADD(hour,13,C.MappingDate))
		   				 else DATEADD(hour,13,C.MappingDate) end as 'FixedMappingDateSZ'
		   				 --doc被mapping的深圳时间（13小时差）
		   				 --美国日期周五并且深圳时间周五18点之后mapping的doc加上两天
			         
						,C.AtivationDate
   						,case when datepart(weekday,C.AtivationDate)=6 and DATEPART(hour,DATEADD(hour,13,C.AtivationDate))>=10 then dateadd(day,2,DATEADD(hour,13,C.AtivationDate))
		   				 else DATEADD(hour,13,C.AtivationDate) end as 'FixedAtivationDateSZ'  
		   				 --contractID被激活的深圳时间（13小时差）
		   				 --美国日期周五并且深圳时间周五10点之后contractID被激活的时间加上两天  
             
				   from (  
						  select d.ProcessId
						 ,sp.Value as'DocumentType'
						 ,d.DocumentDate ,d.CreationDate
						 ,D.AtivationDate as 'AtivationDate'
						 ,(select top 1 mpl.CreationDate 
							 from DocumentAcquisition ..MasterProcessLog as mpl
							 where mpl.[Status] =10
							  and mpl.ProcessId =d.ProcessId
							  and mpl.InvestmentMapping is not null  
							  order by mpl.LogId )as 'MappingDate'
							  from DocumentAcquisition..MasterProcess as d
							  left join DocumentAcquisition..InvestmentMapping AS dim on dim.ProcessId=d.ProcessId
							  left join DocumentAcquisition..VAPolicy as vp on vp.PolicyID=dim.InvestmentId and vp.ContractStatus=0 and vp.IsUse=1
							  left join (
										  SELECT vp1.ContractID, min(case when vot.PreviousValue<>'0' and vot.CurrentValue='0' then vot.LastUpdate end) as 'AtivationDate'
										  FROM DocumentAcquisition..VAPolicy as vp1
										  left join LogData_DMWkspaceDB.dbo.VAOperationTracking as vot on vot.VAId=vp1.ID and vot.DataPoint='ContractStatus'
										  group by vp1.ContractID
											) as D on D.ContractID=vp.ContractID
								left join DocumentAcquisition..QcFundLog as dmt on dmt.ProcessId=d.ProcessId 
								and (dmt.QcRuleId='FDQC000001' and dmt.StatusId=1)
								left join DocumentAcquisition ..SystemParameter as sp on sp.CodeChar =d.DocumentType and sp.CategoryId =105
								--where dateadd(hour,13,d.CreationDate) >= '2016-12-1' and dateadd(hour,13,d.CreationDate) < '2017-1-1'
								where DATEDIFF(MONTH,DATEADD(hour,13,d.CreationDate),GETDATE())=1
								and d.Status <>5 
								and d.Category =2 
								and d.DocumentType<>101
				        
				) as C
		 ) as B
	) as A
	--order by A.ProcessId
) as Z
--where Z.FixedAtivationDateSZ is not null
group by Z.ProcessId,Z.DocumentType,Z.FixedDocumentDateSZ   
			 ,Z.FixedCreationDateSZ
			 ,Z.FixedMappingDateSZ
			 ,Z.CutTime
       		 ,Z.MapTime
			 ,Z.Total
			 ,Z.Time_Flag
			 ,Z.Document_Flag
			 ,Z.Result
order by Z.ProcessId