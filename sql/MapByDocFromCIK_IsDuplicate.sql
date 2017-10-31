select Comment
from DocumentAcquisition..MasterProcess 
where Comment is not null
and ContainerId in (%s)