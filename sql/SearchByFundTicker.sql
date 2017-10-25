select distinct fb.LegalName,fb.FundId,ss.SecId,ss.SecurityName,
	   case ss.Status when 0 then 'Obsolete'
					  when 1 then 'Active'
					  when 2 then 'Pending' end as [Status],
	   ss.Universe,
	   ss.CountryId
from CurrentData..FundBasic fb
left join SecurityData..SecuritySearch ss on ss.FundId=fb.FundId
where lower(fb.LegalName) like '%s%%'
	  and fb.DomicileId like '%%USA'
	  and (ss.Universe like '/CE%%' or ss.Universe like '/OE%%')
order by fb.LegalName,ss.SecId