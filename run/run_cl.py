import sys
from Services.python.IncidentService import IncidentService, Incident
from DigitRecog.python.DigitRecog import MLClassification
from UtilityTools.python.RootNtupleTools import RootNtupleWriterTool, RootNtupleReaderTool, intp_value

from exceptions import BaseException



def main():

  print "hello"
  
  
  root_svc_reader = RootNtupleReaderTool("RootToolReader","tree.root", "ttree", 2)
  
  ml = MLClassification("mlTool",2)
  
  ientry = 0;
  while True:
    try:
      vec = root_svc_reader.GetBranchEntry_DoubleVector("features",ientry)
      targ = root_svc_reader.GetBranchEntry_Int("target", ientry)
    except BaseException as e:
      print "Cauth Error! -> ", str(e)
      break

    if targ == None: break;

    try:
      ml.accumulateTrain(intp_value(targ), vec)
    except BaseException as e:
      print "Cauth Error! -> ", str(e)
      break

    ientry += 1
    if (ientry == 5000): break

  print "read ", ientry, " entries"
  
  if ( ientry != 5000): return 1
  
  
  inc_svc = IncidentService.getInstance()
  root_svc = RootNtupleWriterTool("RootTool", "tree_results.root", "train/ttree", 2)
  ml.setRootNtupleHelper(root_svc)
  
  inc_svc.fireIncident(Incident("BeginRun"))
  
  try:
    ml.performCrossValidationTraining(4,25, 5, 20,100)
  except BaseException as e:
    print "Cauth Error! -> ", str(e)
    inc_svc.fireIncident(Incident("EndRun"))
    return 1

  root_svc.stop() #stop listening to Begin/EndEvent
  #inc_svc.fireIncident(Incident("EndRun"))


  ## bis
  '''
  root_svc_bis = RootNtupleWriterTool("RootToolBis", "tree_results.root", "test/ttree", 3)
  ml.setRootNtupleHelper(root_svc_bis)
  
  inc_svc.fireIncident(Incident("BeginRun"))
  
  try:
    ml.performCrossValidationTraining(4, 25, 5, 20)
  except BaseException as e:
    print "Cauth Error! -> ", str(e)
    inc_svc.fireIncident(Incident("EndRun"))
    return 1
  '''
  
  inc_svc.fireIncident(Incident("EndRun"))

  
  
  
  inc_svc.kill()
  print "here"
  


  return 0

if __name__ == '__main__':
    # main should return 0 for success, something else (usually 1) for error.
    sys.exit(main())

