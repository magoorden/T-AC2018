import sys

assert len(sys.argv)>0
nrTotalWafers = int(sys.argv[1])

c_chuckSwaps = []
u_chuckSwaps = []

for i in range(nrTotalWafers):
  for j in range(nrTotalWafers):
    if i != j and i < j:
      c_chuckSwaps += ["chuckSwap_" + str(i) + "_" + str(j) + "_s"]
      u_chuckSwaps += ["chuckSwap_" + str(i) + "_" + str(j) + "_e"]
      c_chuckSwaps += ["chuckSwap_" + str(j) + "_" + str(i) + "_s"]
      u_chuckSwaps += ["chuckSwap_" + str(j) + "_" + str(i) + "_e"]

print """\ncontrollable void {actions}; """.format(actions=', '.join(c_chuckSwaps))
print """uncontrollable void {actions}; """.format(actions=', '.join(u_chuckSwaps))
