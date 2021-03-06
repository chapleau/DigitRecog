import sys
from Services.python.IncidentService import IncidentService, Incident
from Services.python.Messaging import PyMessaging, logDEBUG, logINFO, logWARNING, logERROR
from UtilityTools.python.RootNtupleTools import RootNtupleWriterTool, RootNtupleReaderTool, intp_value
from UtilityToolsInterfaces.python.ObjectHolder import VectorObjectHolder_Float


from exceptions import BaseException

from scilearn import ClassificationTool

def main():
  

  #Messaging helper tool
  log = PyMessaging("main", logDEBUG)
  toLog = log.PyLOG

  num = 42000
  
  # Reader tool : fetches the features vectors from the ROOT file
  # (one vector of features per event)
  root_svc_reader = RootNtupleReaderTool("RootToolReader","tree.root", "ttree", 2)
  
  # Random Forest Classifier tool
  ml = ClassificationTool("mlTool",num/2, num/2, logDEBUG)
  
  # loop over entries/events in input TTree and feed them to the mlTool
  ientry = 0;
  while True:
    try:
      vec = root_svc_reader.GetBranchEntry_DoubleVector("features",ientry)
      targ = root_svc_reader.GetBranchEntry_Int("target", ientry)
    except BaseException as e:
      toLog("Caught Error reading! -> "+ str(e), logERROR)
      break

    # if EOF reached, stop.
    if targ == None: break
    
    

    # Use 'num/2' events for the training process
    # remaining 'num/2' is for testing
    try:
      ml.accumulateData(intp_value(targ), vec)
    except BaseException as e:
      toLog( "Caught Error! -> " + str(e), logERROR)
      break

    ientry += 1
    if (ientry == num): break

  toLog("read %d entries" % ientry, logINFO)
  toLog("Accumulated %d events" % ml.accumulateData_called, logDEBUG)
  
  # sanity check;
  #   make sure the desired amount of events has been processed before continuing
  if ( ientry != num):
    toLog("Didn't process required amount of events..exiting", logERROR)
    return 1
  
  toLog("%s"% str(ml.train_features().shape), logINFO)

  # results from the training (cross-validation) process are output to a TTree
  root_svc = RootNtupleWriterTool("RootTool", "tree_results_.root", "train/ttree", logINFO)
  ml.setRootNtupleHelper(root_svc)

  inc_svc = IncidentService.getInstance()
  try:
    inc_svc.fireIncident(Incident("BeginRun"))
  except BaseException as e:
    toLog( "Caught Error! -> " + str(e), logERROR)
    inc_svc.kill()
    return 0

  #####
  # Performs the cross-validation (using 500 trees by default)
  #####
  try:
    ml.performCrossValidationTraining(num_trees=500)
  except BaseException as e:
    toLog( "Caught Error! -> " + str(e), logERROR)
    inc_svc.fireIncident(Incident("EndRun"))
    inc_svc.kill()
    return 0

  # we're done, save output
  inc_svc.fireIncident(Incident("EndRun"))
  
  inc_svc.kill()
  
  return 0
  
    
      

  return 0
  
  
  root_svc.stop() #stop listening to Begin/EndEvent

  
  #####
  # Performs the training process on the whole training dataset
  #####
  try:
    ml.performTraining(25, 5, 20)
  except BaseException as e:
    print "Caught Error! -> ", str(e)
    inc_svc.fireIncident(Incident("EndRun"))
    return 1

  
  # results from the testing procedure are saved in a TTree
  root_svc_test = RootNtupleWriterTool("RootToolTest", "tree_results.root", "test/ttree", 2)
  ml.setRootNtupleHelper(root_svc_test)
  
  inc_svc.fireIncident(Incident("BeginRun"))

  #####
  # Performs the testing process
  #####
  try:
    ml.performTesting("train")
  except BaseException as e:
    print "Caught Error! -> ", str(e)
    inc_svc.fireIncident(Incident("EndRun"))
    return 1

  #################

  # we're done, save output
  inc_svc.fireIncident(Incident("EndRun"))
  inc_svc.kill()
  


  return 0

if __name__ == '__main__':
    # main should return 0 for success, something else (usually 1) for error.
    sys.exit(main())


