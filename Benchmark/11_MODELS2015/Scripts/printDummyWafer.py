import sys

assert len(sys.argv)>0

waferId = str(sys.argv[1])

initState = str(sys.argv[2])

numberOfWafers = sys.argv[3]

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
  'PA': ['PA_Align']
}

# == EVENTS ====================================================================

controllableActions = []
uncontrollableActions = []

startSuffix = "_" + waferId + "_s"
endSuffix = "_" + waferId + "_e"

for source in routing.keys():
  for target in routing[source]:
    controllableActions += [source + "to" + target + startSuffix]
    uncontrollableActions += [source + "to" + target + endSuffix]

for act in sum(actions.values(), []):
  controllableActions += [act + startSuffix]
  uncontrollableActions += [act + endSuffix]

print """\ncontrollable {actions}; """.format(actions=', '.join(controllableActions))
print """uncontrollable {actions}; """.format(actions=', '.join(uncontrollableActions))


# == REQUIREMENTS ==============================================================

print """\n// ObsAligned_{i}: alignment status of wafer {i}.
plant ObsAligned_{i}:
  monitor LRtoDU_{i}_s, LRtoPA_{i}_s, LRtoCTC0_{i}_s, CH0toUR_{i}_s, CH1toUR_{i}_s, PAtoUR_{i}_s, SUBtoUR_{i}_s, CTC1toUR_{i}_s, PA_Align_{i}_e;

  location not_aligned:
    initial; marked;
    edge PA_Align_{i}_e goto aligned;
  location aligned:
    marked;
    edge LRtoDU_{i}_s, LRtoPA_{i}_s, LRtoCTC0_{i}_s, CH0toUR_{i}_s, CH1toUR_{i}_s, PAtoUR_{i}_s, SUBtoUR_{i}_s, CTC1toUR_{i}_s goto not_aligned;  
end""".format(i=waferId)

print """\n// ReqAligned_{i}: only aligned wafers can be sent to the wafer stage.
requirement ReqAligned_{i}:
  location:
    initial; marked;
    edge LRtoCH0_{i}_s, LRtoCH1_{i}_s when ObsAligned_{i}.aligned;
end""".format(i=waferId)

# REQ_TR4: Dummy wafers are never send to the track.
print """\n// ReqStayInSystem_{i}: dummy wafers are never send to the track.
requirement ReqStayInSystem_{i}:
  location:
    initial; marked;
    edge DUtoTR_{i}_s when false;
end""".format(i=waferId)



# == PLANT =====================================================================

print """\n// WaferPlant_{i}: wafer plant for production wafer {i}.
plant WaferPlant_{i}:""".format(i = waferId)

for source in routing.keys():
  print """  location %s:
    marked;""" % source
  if source == initState:
    print """    initial;"""
  for target in routing[source]:
    print """    edge {edge}{suffix} goto {edge};""".format(edge=source + "to" + target,suffix=startSuffix)
  if source in actions:
    for cap in actions[source]:
      print """    edge {action}{suffix} goto {edge};""".format(action=cap, edge=cap+"Running",suffix=startSuffix)

# Actions at specific resources.
print ""

for source in routing.keys():
  if source in actions:
    for cap in actions[source]:
      print """  location {action}Running:
    edge {action}{suffix} goto {s};""".format(action=cap, s=source,suffix=endSuffix)

# Transition states.
print ""
for source in routing.keys():
  for target in routing[source]:
    print """  location {edge}:
    edge {edge}{suffix} goto {target};""".format(edge=source + "to" + target,target=target,suffix=endSuffix)

print """end"""
