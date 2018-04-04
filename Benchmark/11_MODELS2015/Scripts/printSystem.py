import sys

assert len(sys.argv)>0
nrProdWafers = int(sys.argv[1])
nrTotalWafers = int(sys.argv[2])

print """// Star interfaces for the resources.
import "Resources.cif";

// System plant and requirement models.
import "SystemPlant.cif";
import "SystemReq.cif";

// Wafer plant and requirement models."""

for i in range(nrTotalWafers):
  print """import "Wafer%s.cif";""" % str(i)
