
------------------------------------
--Author:        Viki Chen
--CreationDate:  2017-10-30
--RevisedDate:   2017-11-08
------------------------------------

--A:    取完成QC的时间点等各种时间点
--B:    将A中的各种时间点转为深圳时间并Fix掉周末及非工作时间
--C：   计算B中的各个时间的差值，算出完成各个QC所用的时间长度CutTime,ChartTime,MapTime,LinkTime（小于等于'0'的结果都计'0'）
--D:    根据C结果，以ProcessId为单位选出完成QC所用时间长度的最大值
--E：   根据D结果，以ProcessId为单位返回用时间最长的QC（Cut,Chart,Map,Link）,并将MapTime&ChartTime合并为一列（选较大值）
--F:    将E中的CutTime,Chart/MapTime,LinkTime的数据类型换成浮点数，以小时为单位记录QC所用时间长度；并根据E结果，返回各个QCOwner
--表层：根据F，加总各个QC用时的和，并限制跑出的结果是时间总和>24小时的Doc

--CreationDate,CharttingDate,MappingDate,CompleteLinkDate为完成QC的时间点
--CutTime,ChartTime,MapTime,LinkTime为完成QC所用的时间长度
--后缀为'-SZ'代表已转换为深圳时间（'CreationDateSZ' 即：深圳时间的CreationDate）
--前缀为'Fixed-'代表已调整过周末和非工作时间（'FixedMappingDateSZ' 即：已调整过周末及非工作时间的深圳时间的MappingDate）
--ProcessTime为各个QC所用时间长度中最长的一个（时间长度）
--QC为ProcessTime对应的QC，即用时最长的QC（Cut,Chart/Map,Link)
--Owner为用时最长的QC对应的Cutter/Charter/Mapper/Linker


select datepart(year,F.CreationDateSZ) as [Year],datepart(MONTH,F.CreationDateSZ) as [Month],F.ProcessId,F.DocType,
       F.CutTime,F.[Chart/MapTime],F.LinkTime,(F.CutTime+F.[Chart/MapTime]+F.LinkTime) as 'Total',
       case when (F.CutTime+F.[Chart/MapTime]+F.LinkTime)> 24 then '>24BHr' 
	        else '<=24BHr' end as 'Flag',
	   F.QC,F.[Owner],F.[DocumentDate],
       F.[FixedDocumentDateSZ],F.CreationDate,F.CreationDateSZ,F.FixedCreationDateSZ,
       F.ChartingDate,F.ChartingDateSZ,F.MappingDate,F.MappingDateSZ,F.FixedMappingDateSZ,
       F.TriggerDate,F.TriggerDateSZ,F.FixedTriggerDateSZ,F.CompleteLinkDate,F.CompleteLinkDateSZ
from(
     select E.ProcessId,E.DocType,round(cast(E.CutTime as float)/60,2) as 'CutTime',
			round(cast(E.[Chart/MapTime] as float)/60,2) as 'Chart/MapTime',
			round(cast(E.LinkTime as float)/60,2) as 'LinkTime',E.QC,
			
			--当QC='Cut'时，取表MasterProcess中DA2为'Owner'
			(case when E.QC='Cut'then (select cut.Email from DocumentAcquisition ..MasterProcess as mpc 
			                           left join DocumentAcquisition ..Account as cut on cut.DaId =mpc.DA2 
									   where mpc.ProcessId=E.ProcessId)
			--当QC='Chart'时，取表DocumentChartTracking中LastUpdate最早且加过图的UserId
			      when E.QC='Chart' then (select top 1 chart.Email from DocumentAcquisition ..DocumentChartTracking as ct 
				                          left join DocumentAcquisition ..Account as chart on chart.DaId =ct.UserId 
										  where ct.AddChart=1 and E.ProcessId =ct.DocumentId 
										  order by ct.LastUpdate)
			--当QC='Map'时，取表MasterProcessLog中LogId最小（时间最早）且完成了Mapping的UpdateUserId为'Owner'   
				  when E.QC='Map' then (select top 1 Map.Email from DocumentAcquisition..MasterProcessLog as mpl 
				                        left join DocumentAcquisition ..Account as Map on Map.DaId =mpl.UpdateUserId 
										where E.ProcessId=mpl.ProcessId and mpl.[Status]=10 
										order by mpl.LogId)
			--当QC='Link'时，取表DocumentDataNode中AddAnchorUser为'Owner'
			      when E.QC='Link'then (select link.Email from DocumentAcquisition ..DocumentDataNode as dn 
				                        left join DocumentAcquisition ..Account as link on link.DaId =dn.AddAnchorUser 
										where dn.ProcessId=E.ProcessId)
			      end)as 'Owner',
				  
			E.[DocumentDate],E.[FixedDocumentDateSZ],E.CreationDate,E.CreationDateSZ,E.FixedCreationDateSZ,
			E.ChartingDate,E.ChartingDateSZ,E.MappingDate,E.MappingDateSZ,E.FixedMappingDateSZ,E.TriggerDate,
			E.TriggerDateSZ,E.FixedTriggerDateSZ,E.CompleteLinkDate,E.CompleteLinkDateSZ
     from(
	      select D.ProcessId,D.DocumentId,D.DocumentDate,D.DocType,D.CutTime,D.LinkTime,D.FixedDocumentDateSZ,
		         D.CreationDate,D.CreationDateSZ,D.FixedCreationDateSZ,D.ChartingDate,D.ChartingDateSZ,D.MappingDate,
				 D.MappingDateSZ,D.FixedMappingDateSZ,D.TriggerDate,D.TriggerDateSZ,
				 D.FixedTriggerDateSZ,D.CompleteLinkDate,D.CompleteLinkDateSZ,
				 
				 --E 当ChartTime > MapTime时，返回ChartTime；（MapTime&ChartTime间选时间更大的为'Char/Map'）,
			     (case when D.[ChartTime]>D.MapTime then D.ChartTime
			     --E 当MapTime > ChartTime时，返回MapTime；
			           when D.MapTime>=D.ChartTime then D.MapTime
			           end)as 'Chart/MapTime',
			     --E 当ProcessTime（Max（Time））=CutTime，则返回'Cut'； 
			     (case when D.ProcessTime=D.CutTime then 'Cut'
			     --E 当ProcessTime=ChartTime,则返回'Chart'
			           when D.ProcessTime=D.ChartTime then 'Chart'
			     --E 当ProcessTime=MapTime,则返回'Map'
			           when D.ProcessTime=D.MapTime then 'Map'
			     --E 当ProcessTime=LinkTime，则返回'Link'
			           when D.ProcessTime=D.LinkTime then 'Link'
			     --E 命名为'QC'（导致Timeliness的QC）
			           end) as 'QC'
          from( 
		       select C.ProcessId,C.DocumentId,C.DocumentDate,C.DocType,C.CutTime,C.ChartTime,C.MapTime,C.LinkTime,
			          C.FixedDocumentDateSZ,C.CreationDate,C.CreationDateSZ,C.FixedCreationDateSZ,C.ChartingDate,
					  C.ChartingDateSZ,C.MappingDate,C.MappingDateSZ,C.FixedMappingDateSZ,C.TriggerDate,
					  C.TriggerDateSZ,C.FixedTriggerDateSZ,C.CompleteLinkDate,C.CompleteLinkDateSZ,
                      --D（选取CutTime，ChartTime，MapTime，LinkTime中的最大值为ProcessTime）
                      (select MAX(ProcessTime)from (values(C.CutTime),(C.ChartTime),(C.MapTime),(C.LinkTime))as ProcessTime (ProcessTime))as 'ProcessTime' 
          
               from( 
			        select B.ProcessId,B.DocumentId,B.DocumentDate,B.DocType,
						   B.FixedDocumentDateSZ,B.CreationDate,B.CreationDateSZ,B.FixedCreationDateSZ,B.ChartingDate,
						   B.ChartingDateSZ,B.MappingDate,B.MappingDateSZ,B.FixedMappingDateSZ,B.TriggerDate,
						   B.TriggerDateSZ,B.FixedTriggerDateSZ,B.CompleteLinkDate,B.CompleteLinkDateSZ,
						   
						   --C（当Fix后深圳时间的CreationDate减去Fix后深圳时间的DocumentDate大于0时，则取CreationDate减去DocumentDate的差值为CutTime，否则CutTime=0）
						   (case when datediff(MINUTE,B.FixedDocumentDateSZ,B.FixedCreationDateSZ)>0 then datediff(MINUTE,B.FixedDocumentDateSZ,B.FixedCreationDateSZ)else 0 end) as 'CutTime',
						   --C（当深圳时间的ChartingDate减去Fix后深圳时间的CreationDate大于0时，则取其为ChartTime，否则取0）
						   (case when datediff(MINUTE,B.FixedCreationDateSZ,B.ChartingDateSZ)>0 then datediff(MINUTE,B.FixedCreationDateSZ,B.ChartingDateSZ)else 0 end) as 'ChartTime',
						   --C（当Fix后深圳时间的MappingDate减去Fix后深圳时间的CreationDate大于0时，则取其为MappingDate，否则取0）
						   (case when datediff(MINUTE,B.FixedCreationDateSZ,B.FixedMappingDateSZ)>0 then datediff(MINUTE,B.FixedCreationDateSZ,B.FixedMappingDateSZ)else 0 end) as 'MapTime',
						   --C （当深圳时间的CompleteLinkDate减去Fix后深圳时间的TriggerTime大于0时，则取其为LinkTime，否则取0）
						   (case when datediff(MINUTE,B.FixedTriggerDateSZ,B.CompleteLinkDateSZ)>0 then datediff(MINUTE,B.FixedTriggerDateSZ,B.CompleteLinkDateSZ) else 0 end)as 'LinkTime'
               
					from(
						 select A.ProcessId,A.DocumentId,A.DocType,A.DocumentDate,
						 
								 --B（当DocumentDate是美国时间的周五0时0分，则Fix为深圳时间周一上午9点（+2天周末,再+33小时改为深圳时间上午9点） 
								 case when datepart(weekday,A.DocumentDate)=6 then dateadd(day,2,DATEADD(hour,33,A.DocumentDate))
								 --B（否则DocumentDate不变，取深圳时间上午9点)
									  else DATEADD(hour,33,A.DocumentDate) end as 'FixedDocumentDateSZ',
									  
								 A.CreationDate,
								 DATEADD(hour,13,A.CreationDate)as 'CreationDateSZ',
								 
								 --B（当CreationDate是深圳时间周一至周四下午18点之后，则Fix为次日上午9点）
								 case when DATEPART(weekday,DATEADD(hour,13,A.CreationDate))in (2,3,4,5) and DATEPART(hour,DATEADD(hour,13,A.CreationDate))>=18 then dateadd(hour,9,cast(convert(char(10),DATEADD(day,1,DATEADD(hour,13,A.CreationDate)),120) as datetime))
								 --B（当CreationDate是深圳时间周一至周四上午9点之前，则Fix为当日9点）
									  when DATEPART(weekday,DATEADD(hour,13,A.CreationDate))in (2,3,4,5,6) and DATEPART(hour,DATEADD(hour,13,A.CreationDate))<9 then dateadd(hour,9,cast(convert(char(10),DATEADD(hour,13,A.CreationDate),120) as datetime))
								 --B（当CreationDate是深圳时间周五下午18点及之后，则Fix为三天后（下周一）上午9点）
									  when DATEPART (weekday,DATEADD(hour,13,A.CreationDate))=6 and DATEPART (hour,DATEADD(hour,13,A.CreationDate))>=18 then dateadd(hour,9,cast(convert(char(10),dateadd(day,3,DATEADD(hour,13,A.CreationDate)),120)as datetime))
								 --B（当CreationDate是深圳时间的周六，则Fix为两天后（下周一）上午9点）
									  when DATEPART (weekday,DATEADD(hour,13,A.CreationDate))=7 then dateadd(hour,9,CAST(CONVERT(char(10),dateadd(day,2,dateadd(hour,13,A.CreationDate)),120)as datetime))
								 --B（当CreationDate是深圳时间周日，则Fix为次日（周一）上午9点）
									  when DATEPART (weekday,DATEADD(hour,13,A.CreationDate))=1 then dateadd(hour,9,CAST(CONVERT(char(10),dateadd(day,1,dateadd(hour,13,A.CreationDate)),120)as datetime))
								 --B（否则CreationDate不变，取深圳时间）
									  else DATEADD(hour,13,A.CreationDate) end as 'FixedCreationDateSZ',
									  
								 A.ChartingDate,DATEADD(hour,13,A.ChartingDate) as 'ChartingDateSZ',A.MappingDate,
								 DATEADD(hour,13,A.MappingDate) as 'MappingDateSZ',
								
								 --B（当MappingDate是深圳时间周一至周四下午18点之后，则Fix为次日上午9点）
								 case when DATEPART(weekday,DATEADD(hour,13,A.MappingDate))in (2,3,4,5) and DATEPART(hour,DATEADD(hour,13,A.MappingDate))>=18 then dateadd(hour,9,cast(convert(char(10),DATEADD(day,1,DATEADD(hour,13,A.MappingDate)),120) as datetime))
								 --B（当MappingDate是深圳时间周一至周四上午9点之前，则Fix为当日9点)
									  when DATEPART(weekday,DATEADD(hour,13,A.MappingDate))in (2,3,4,5,6) and DATEPART(hour,DATEADD(hour,13,A.MappingDate))<9 then dateadd(hour,9,cast(convert(char(10),DATEADD(hour,13,A.MappingDate),120) as datetime))
								 --B（当MappingDate是深圳时间周五下午18点及之后，则Fix为三天后（下周一）上午9点）
									  when DATEPART (weekday,DATEADD(hour,13,A.MappingDate))=6 and DATEPART (hour,DATEADD(hour,13,A.MappingDate))>=18 then dateadd(hour,9,cast(convert(char(10),dateadd(day,3,DATEADD(hour,13,A.MappingDate)),120)as datetime))
								 --B（当MappingDate是深圳时间的周六，则Fix为两天后（下周一）上午9点）
									  when DATEPART (weekday,DATEADD(hour,13,A.MappingDate))=7 then dateadd(hour,9,CAST(CONVERT(char(10),dateadd(day,2,dateadd(hour,13,A.MappingDate)),120)as datetime))
								 --B（当TriggerTime是深圳时间周日，则Fix为次日（周一）上午9点）
									  when DATEPART (weekday,DATEADD(hour,13,A.MappingDate))=1 then dateadd(hour,9,CAST(CONVERT(char(10),dateadd(day,1,dateadd(hour,13,A.MappingDate)),120)as datetime))
								 --B（否则MappingDate不变，取深圳时间）
									  else DATEADD(hour,13,A.MappingDate) end as 'FixedMappingDateSZ',
									  
								 A.TriggerDate,DATEADD(hour,13,A.TriggerDate) as 'TriggerDateSZ'

								 --B（当TriggerTime是深圳时间周一至周四下午18点及之后，则Fix为次日上午9点）
								,case when DATEPART(weekday,DATEADD(hour,13,A.TriggerDate))in (2,3,4,5) and DATEPART(hour,DATEADD(hour,13,A.TriggerDate))>=18 then dateadd(hour,9,cast(convert(char(10),DATEADD(day,1,DATEADD(hour,13,A.TriggerDate)),120) as datetime))
								 --B（当TriggerTime是深圳时间周一至周四上午9点之前，则Fix为当日9点）
									   when DATEPART(weekday,DATEADD(hour,13,A.TriggerDate))in (2,3,4,5,6) and DATEPART(hour,DATEADD(hour,13,A.TriggerDate))<9 then dateadd(hour,9,cast(convert(char(10),DATEADD(hour,13,A.TriggerDate),120) as datetime))
								 --B（当triggerTime是深圳时间周五下午18点及之后，则Fix为三天后（下周一）上午9点）
									   when DATEPART (weekday,DATEADD(hour,13,A.TriggerDate))=6 and DATEPART (hour,DATEADD(hour,13,A.TriggerDate))>=18 then dateadd(hour,9,cast(convert(char(10),dateadd(day,3,DATEADD(hour,13,A.TriggerDate)),120)as datetime))
								 --B（当TriggerTime是深圳时间的周六，则Fix为两天后（下周一）上午9点）
									   when DATEPART (weekday,DATEADD(hour,13,A.TriggerDate))=7 then dateadd(hour,9,CAST(CONVERT(char(10),dateadd(day,2,dateadd(hour,13,A.TriggerDate)),120)as datetime))
								 --B（当TriggerTime是深圳时间周日，则Fix为次日（周一）上午9点）
									   when DATEPART (weekday,DATEADD(hour,13,A.TriggerDate))=1 then dateadd(hour,9,CAST(CONVERT(char(10),dateadd(day,1,dateadd(hour,13,A.TriggerDate)),120)as datetime))
								 --B（否则TriggerTime不变，取深圳时间）
									   else DATEADD(hour,13,A.TriggerDate) end as 'FixedTriggerDateSZ',
									   
								 A.CompleteLinkDate,DATEADD(hour,13,A.CompleteLinkDate) as 'CompleteLinkDateSZ'
						
						from(
							  --A（取第一次完成加图的时间点为'ChartingDate'）
							  select mp.ProcessId,mp.DocumentId,mp.DocumentDate,sp.Value AS'DocType',mp.CreationDate,
									 (select top 1 ct.LastUpdate 
									  from DocumentAcquisition ..DocumentChartTracking as ct
									  where ct.AddChart=1 and ct.DocumentId =mp.ProcessId 
									  order by ct.LastUpdate )as 'ChartingDate',
									  --A（取Doc第一次Commplete Mapping 的时间点为'MappingDate'）
									  (select top 1 mpl.CreationDate 
									   from DocumentAcquisition ..MasterProcessLog as mpl
									   where mpl.[Status] =10 and mpl.ProcessId =mp.ProcessId 
									   order by mpl.LogId )as 'MappingDate',

									  (select dn.TriggerTime 
									   from DocumentAcquisition ..DocumentDataNode as dn
									   where dn.ProcessId =mp.ProcessId) as 'TriggerDate',

									  (select dn.CompleteLinkTime
									   from DocumentAcquisition ..DocumentDataNode as dn1
									   where dn1.ProcessId =mp.ProcessId) as 'CompleteLinkDate'
											  
							  from DocumentAcquisition ..MasterProcess as mp
							  left join DocumentAcquisition ..SystemParameter as sp on sp.CodeChar =mp.DocumentType and sp.CategoryId =105
							  left join DocumentAcquisition ..DocumentDataNode as dn on dn.ProcessId =mp.ProcessId 
							  where dateadd(hour,13,mp.CreationDate) >= '2016-11-19' 
							        --（时间限制：跑上一个月的Timeliness数据）
									--datediff(MONTH,dateadd(hour,13,mp.CreationDate ),GETDATE() )=1
									and mp.Status=10 and mp.Category =1 and mp.DocumentType not in (73) and mp.Format<>'PDF'
							  
						    ) as A
					    ) as B
				    )as C
			    )as D
		    )as E
		)as F  
             
--选择完成时间超过24小时（TimeLiness Delay）的Doc
--Where (F.CutTime+F.[Chart/MapTime]+F.LinkTime)> 24 
order by datepart(year,F.CreationDateSZ),datepart(MONTH,F.CreationDateSZ)
