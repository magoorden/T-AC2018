import sys
from collections import defaultdict

assert len(sys.argv)>0
nrProdWafers = int(sys.argv[1])
nrTotalWafers = int(sys.argv[2])

# Wafer routing possibilities.
routing = {
  'TR': ['SUB'],
  'SUB': ['UR'],
  'UR': ['SUB','DU','PA','CTC1'],
  'PA': ['UR','LR'],
  'LR': ['DU','PA','CH0','CH1','CTC0'],
  'DU': ['UR','LR','TR'],
  'CH0': ['LR','UR'],
  'CH1': ['LR','UR'],
  'CTC0': ['LR'],
  'CTC1': ['UR']
}

actions = {
  'SUB': ['SUB_Condition'],
  'PA': ['PA_Align'],
  'CH0': ['CH0_Measure','CH0_Expose'],
  'CH1': ['CH1_Measure','CH1_Expose']
}

actionsDummy = {
  'PA': ['PA_Align'],
}

values = set(a for b in routing.values() for a in b)
reverseRouting = dict((new_key, [key for key,value in routing.items() if new_key in value]) for new_key in values)


print """import "System.cif";"""

# Breaking the water.
print """\n// Avoid breaking the wafer.
requirement ReqBreakingWater:
  location:
    initial; marked;
    edge breakWater when false;
end"""

# FIFO: FI.
print """\n// ReqFIFO (a): In-order
requirement ReqFIFO_in:"""
for i in range(nrProdWafers):
  print "  location l{i}:".format(i=i)
  if i == 0:
    print "    marked; initial;"
  print "    edge TRtoSUB_{i}_s goto l{next};".format(i=i,next=(i+1)%nrProdWafers)
print """end"""

# FIFO: FO
print """\n// ReqFIFO (b): Out-order
requirement ReqFIFO_out:"""
for i in range(nrProdWafers):
  print "  location l{i}:".format(i=i)
  if i == 0:
    print "    marked; initial;"
  print "    edge DUtoTR_{i}_s goto l{next};".format(i=i,next=(i+1)%nrProdWafers)
print """end"""

print """\n// ReqOccupied: wafer place status for each resource."""

for resource in reverseRouting.keys():
  if resource == 'TR':
    continue

  occupiedList = []
  freeList = []

  for waferId in range(nrTotalWafers):
    startSuffix = "_" + str(waferId) + "_s"
    endSuffix = "_" + str(waferId) + "_e"
    occupiedList += [source + "to" + resource + startSuffix for source in reverseRouting[resource]]
    freeList += [resource + "to" + target + startSuffix for target in routing[resource]]

  print """requirement ReqOccupied_%s:""" % resource
  print """  location free:"""
  if resource != 'CH0' and resource != 'CH1': 
    print "    marked; initial;"
  print """    edge {occupiedList} goto occupied;
  location occupied:""".format(occupiedList=', '.join(occupiedList))
  if resource == 'CH0' or resource == 'CH1': 
    print "    marked; initial;"
  print """    edge {emptyList} goto free;""".format(emptyList=', '.join(freeList))
  print """end\n"""
