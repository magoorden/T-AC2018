import sys

assert len(sys.argv)>0
nrProdWafers = int(sys.argv[1])
nrTotalWafers = int(sys.argv[2])

# Wafer operations on CH0.
listCH0_Measure = ["CH0_Measure_%s_s" % str(i) for i in range(nrProdWafers)] 
listCH0_Expose = ["CH0_Expose_%s_s" % str(i) for i in range(nrProdWafers)] 

# Wafer operations on CH1.
listCH1_Measure = ["CH1_Measure_%s_s" % str(i) for i in range(nrProdWafers)] 
listCH1_Expose = ["CH1_Expose_%s_s" % str(i) for i in range(nrProdWafers)] 

# Wafer moves from and to CH0.
listCH0_moves = ["CH0toLR_%s_s" % str(i) for i in range(nrProdWafers+2)]
listCH0_moves += ["LRtoCH0_%s_s" % str(i) for i in range(nrProdWafers+2)]
listCH0_moves += ["CH0toUR_%s_s" % str(i) for i in range(nrProdWafers+2)]

# Wafer moves from and to CH1.
listCH1_moves = ["CH1toLR_%s_s" % str(i) for i in range(nrProdWafers+2)]
listCH1_moves += ["LRtoCH1_%s_s" % str(i) for i in range(nrProdWafers+2)]
listCH1_moves += ["CH1toUR_%s_s" % str(i) for i in range(nrProdWafers+2)]

print """import "System.cif";"""

print """
controllable chuckSwap_s;
uncontrollable chuckSwap_e, breakWater;"""

print """
// PositionChucks: physical position of the chucks.
plant PositionCH0:
  location atExpose:
    marked; initial;
    edge chuckSwap_s goto ExposeToMeasure;
  location atMeasure:
    edge chuckSwap_s goto MeasureToExpose;

  location ExposeToMeasure:
    edge chuckSwap_e goto atMeasure;
  location MeasureToExpose:
    edge chuckSwap_e goto atExpose;
end"""

print """
plant PositionCH1:
  location atExpose:
    edge chuckSwap_s goto ExposeToMeasure;
  location atMeasure:
    marked; initial;
    edge chuckSwap_s goto MeasureToExpose;

  location ExposeToMeasure:
    edge chuckSwap_e goto atMeasure;
  location MeasureToExpose:
    edge chuckSwap_e goto atExpose;
end"""

print """
// ActionChucks: actions allowed on the chucks.
plant ActionsCH0:
  location:
    initial; marked;
    edge {CH0Expose} when PositionCH0.atExpose;
    edge {CH0Measure} when PositionCH0.atMeasure;
    edge {CH0Moves} when PositionCH0.atMeasure;
end""".format(CH0Measure=', '.join(listCH0_Measure),CH0Moves=', '.join(listCH0_moves),CH0Expose=', '.join(listCH0_Expose))

print """
plant ActionsCH1:
  location:
    initial; marked;
    edge {CH1Expose} when PositionCH1.atExpose;
    edge {CH1Measure} when PositionCH1.atMeasure;
    edge {CH1Moves} when PositionCH1.atMeasure;
end""".format(CH1Measure=', '.join(listCH1_Measure),CH1Moves=', '.join(listCH1_moves),CH1Expose=', '.join(listCH1_Expose))

print """
plant BreakWater:
  location:
    initial; marked;
    edge breakWater when (PositionCH0.atExpose and ReqOccupied_CH0.free) or (PositionCH1.atExpose and ReqOccupied_CH1.free);
end"""

print """
// ChuckDedAssignment: Chuck dedication assignment is only done for the wafer 
// that is next to be send to the system.
plant ChuckDedAssignment:"""
for i in range(nrProdWafers):
  print "  location l{i}:".format(i=i)
  if i == 0:
    print "    marked; initial;"
  print "    edge assignCH0_{i}, assignCH1_{i}, assignCH0orCH1_{i};".format(i=i,next=(i+1)%nrProdWafers)
  print "    edge TRtoSUB_{i}_s goto l{next};".format(i=i,next=(i+1)%nrProdWafers)
print """end"""
