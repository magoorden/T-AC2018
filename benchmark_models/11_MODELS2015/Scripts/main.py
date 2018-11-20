import os
import subprocess
import sys

def generateSystem(nrProdWafers):
  # Total number of wafers = number of production wafers + 2 dummy wafers.
  nrTotalWafers = nrProdWafers + 2

  # Generate directory.
  directory = "generated/" + str(nrProdWafers)
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Write wafers to file.
  for i in range(nrProdWafers):
    with open("%s/Wafer%s.cif" % (directory, str(i)), "w+") as output:
      subprocess.call(["python", "printWafer.py", str(i), str(nrTotalWafers)], stdout=output);

  # Write dummy wafers to file.
  with open("%s/Wafer%s.cif" % (directory, str(nrProdWafers)), "w+") as output:
    subprocess.call(["python", "printDummyWafer.py", str(nrProdWafers), 'CH0', str(nrTotalWafers)], stdout=output);
  with open("%s/Wafer%s.cif" % (directory, str(nrProdWafers+1)), "w+") as output:
    subprocess.call(["python", "printDummyWafer.py", str(nrProdWafers+1), 'CH1', str(nrTotalWafers)], stdout=output);

  # Write resources to file.
  with open("%s/Resources.cif" % directory, "w+") as output:
    subprocess.call(["python", "printResources.py", str(nrProdWafers)], stdout=output);

  # Write system to file.
  with open("%s/System.cif" % directory, "w+") as output:
    subprocess.call(["python", "printSystem.py", str(nrProdWafers), str(nrTotalWafers)], stdout=output);

  # Write system plant to file.
  with open("%s/SystemPlant.cif" % directory, "w+") as output:
    subprocess.call(["python", "printSystemPlant.py", str(nrProdWafers), str(nrTotalWafers)], stdout=output);
  
  # Write system requirements to file.
  with open("%s/SystemReq.cif" % directory, "w+") as output:
    subprocess.call(["python", "printSystemReq.py", str(nrProdWafers), str(nrTotalWafers)], stdout=output);

  # Write type definitions to file.
  with open("%s/Types.cif" % directory, "w+") as output:
    subprocess.call(["python", "printTypes.py"], stdout=output);

generateSystem(int(sys.argv[1]))
