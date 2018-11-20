import sys

assert len(sys.argv)>0

waferId = str(sys.argv[1])

nrTotalWafers = sys.argv[2]

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

initState = 'TR'

actions = {
  'SUB': ['SUB_Condition'],
  'PA': ['PA_Align'],
  'CH0': ['CH0_Measure','CH0_Expose'],
  'CH1': ['CH1_Measure','CH1_Expose']
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

# Chuck dedication events.
uncontrollableActions += ["assignCH0_" + waferId]
uncontrollableActions += ["assignCH1_" + waferId]
uncontrollableActions += ["assignCH0orCH1_" + waferId]

print """controllable {actions}; """.format(actions=', '.join(controllableActions))
print """uncontrollable {actions}; """.format(actions=', '.join(uncontrollableActions))


# == REQUIREMENTS ==============================================================

print """
import "Types.cif";"""

# Wafer life cycle.
print """
// ReqLifeCycle_{i}: production wafer life cycle requirement.
requirement ReqLifeCycle_{i}:
  location l0:
    initial; marked;
    edge TRtoSUB_{i}_e goto l1;
  location l1:
    edge SUB_Condition_{i}_s goto l2;
  location l2:
    edge SUB_Condition_{i}_e goto l3;
  location l3:
    edge PA_Align_{i}_s goto l4;
  location l4:
    edge PA_Align_{i}_e goto l5;
  location l5:
    edge PA_Align_{i}_s goto l4;
    edge CH0_Measure_{i}_s, CH1_Measure_{i}_s goto l6;
  location l6:
    edge CH0_Measure_{i}_e, CH1_Measure_{i}_e goto l7;
  location l7:
    edge CH0_Expose_{i}_s, CH1_Expose_{i}_s goto l8;
  location l8:
    edge CH0_Expose_{i}_e, CH1_Expose_{i}_e goto l9;
  location l9:
    edge DUtoTR_{i}_s goto l0;  
end""".format(i=waferId)

# Wafer alignment.
print """
// ObsAligned_{i}: alignment status of wafer {i}.
plant ObsAligned_{i}:
  monitor LRtoDU_{i}_s, LRtoPA_{i}_s, LRtoCTC0_{i}_s, CH0toUR_{i}_s, CH1toUR_{i}_s, PAtoUR_{i}_s, SUBtoUR_{i}_s, CTC1toUR_{i}_s, PA_Align_{i}_e;

  location not_aligned:
    initial; marked;
    edge PA_Align_{i}_e goto aligned;
  location aligned:
    marked;
    edge LRtoDU_{i}_s, LRtoPA_{i}_s, LRtoCTC0_{i}_s, CH0toUR_{i}_s, CH1toUR_{i}_s, PAtoUR_{i}_s, SUBtoUR_{i}_s, CTC1toUR_{i}_s goto not_aligned;  
end""".format(i=waferId)

print """
// ReqAligned_{i}: only aligned wafers can be sent to the wafer stage.
requirement ReqAligned_{i}:
  location:
    initial; marked;
    edge LRtoCH0_{i}_s, LRtoCH1_{i}_s when ObsAligned_{i}.aligned;
end""".format(i=waferId)

# Chuck dedication.
print """
// ObsChuckDed_{i}: chuck dedication status of wafer {i}.
plant ObsChuckDed_{i}:
  disc ChuckDedicationType dedication = Unknown;
  monitor assignCH0_{i}, assignCH1_{i}, assignCH0orCH1_{i};

  location assignedNo:
    initial; marked;
    edge assignCH0_{i} do dedication := DedicatedToCH0 goto assignedYes;
    edge assignCH1_{i} do dedication := DedicatedToCH1 goto assignedYes;
    edge assignCH0orCH1_{i} do dedication := NoChuckDedication goto assignedYes;
  location assignedYes:
    marked;
    edge DUtoTR_{i}_s do dedication := Unknown goto assignedNo;  
end""".format(i=waferId)


print """
// ReqChuckDed_{i}: measurement and exposure are only allowed on a dedicated chuck.
requirement ReqChuckDed_{i}:
  location:
    initial; marked;
    edge CH0_Measure_{i}_s, CH0_Expose_{i}_s when ObsChuckDed_{i}.dedication = DedicatedToCH0 or ObsChuckDed_{i}.dedication = NoChuckDedication;
    edge CH1_Measure_{i}_s, CH1_Expose_{i}_s when ObsChuckDed_{i}.dedication = DedicatedToCH1 or ObsChuckDed_{i}.dedication = NoChuckDedication;
end""".format(i=waferId)

print """
// AssignChuckDed_{i}: chuck assignment is done before entering the system.
plant AssignChuckDed_{i}:
  location l0:
    initial; marked;
    edge assignCH0_{i}, assignCH1_{i}, assignCH0orCH1_{i} goto l1;
  location l1:
    edge TRtoSUB_{i}_s goto l0;
end""".format(i=waferId)

# == PLANT =====================================================================

print """
// WaferPlant_{i}: wafer plant for production wafer {i}.
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
  if source == 'TR':
    print """    edge assignCH0_{i}, assignCH1_{i}, assignCH0orCH1_{i};""".format(i=waferId)

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
