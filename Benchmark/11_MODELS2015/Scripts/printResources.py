import sys
from collections import defaultdict

assert len(sys.argv)>0

nrProdWafers = int(sys.argv[1])

# Wafer routing possibilities.

resources = ['TR','SUB','UR','PA','LR','DU','CH0','CH1','CTC0','CTC1']

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

startSuffix = "_s"
endSuffix = "_e"

values = set(a for b in routing.values() for a in b)
reverseRouting = dict((new_key, [key for key,value in routing.items() if new_key in value]) for new_key in values)

def updateDict(dic, key, val):
  if key in dic.keys():
    dic[key].append(val)
  else:
    dic[key] = [val]

# == PLANT =====================================================================

print """import "System.cif";"""

def createEventList(event, suffix, n):
  return [event + '_' + str(i) + suffix for i in range(n)]

for r in resources:
  edgeMap = {}
  # Outgoing edges.  
  for target in routing[r]:
    event = r + 'to' + target
    edgeList = createEventList(event, startSuffix, nrProdWafers+2)
    targetState = event
    updateDict(edgeMap, 'l0', (edgeList,targetState))

    edgeEndList = createEventList(event, endSuffix, nrProdWafers+2)
    sourceState = event
    updateDict(edgeMap, sourceState, (edgeEndList,'l0'))

  # Incoming edges.
  for source in reverseRouting[r]:
    event = source + 'to' + r
    edgeList = createEventList(event, startSuffix, nrProdWafers+2)
    targetState = event
    updateDict(edgeMap, 'l0', (edgeList,targetState))

    edgeEndList = createEventList(event, endSuffix, nrProdWafers+2)
    sourceState = event
    updateDict(edgeMap, sourceState, (edgeEndList,'l0'))

  # Actions.
  if r in actions:
    for act in actions[r]:
      # TODO: change this ugly hard coding.
      if act == 'PA_Align':
        n = nrProdWafers+2
      else:
        n = nrProdWafers
      edgeList = createEventList(act, startSuffix, n)
      targetState = act
      updateDict(edgeMap, 'l0', (edgeList,targetState))

      edgeEndList = createEventList(act, endSuffix, n)
      updateDict(edgeMap, targetState, (edgeEndList,'l0'))

  # Chuck dedication.
  if r == 'TR':
    edgeList = []
    edgeList += createEventList('assignCH0', '', nrProdWafers)
    edgeList += createEventList('assignCH1', '', nrProdWafers)
    edgeList += createEventList('assignCH0orCH1', '', nrProdWafers)
    targetState = 'l0'
    updateDict(edgeMap, 'l0', (edgeList,targetState))

  # Chuck swaps
  if r == 'CH0' or r == 'CH1':
    targetState = 'ChuckSwap'
    edgeList = ['chuckSwap_s']
    updateDict(edgeMap, 'l0', (edgeList,targetState))
    edgeEndList = ['chuckSwap_e']
    updateDict(edgeMap, targetState, (edgeEndList,'l0'))
   

  # Initial state.
  print """\nplant P_{res}:""".format(res=r)
  for loc in edgeMap:
    print """  location {loc}:""".format(loc=loc)
    if loc == 'l0':
      print """    initial; marked;"""
    for (edge,target) in edgeMap[loc]:
      print """    edge {edgeList} goto {target};""".format(edgeList=', '.join(edge),target=target)
  print """end"""
