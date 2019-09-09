import sys
import argparse
#sys.path.insert(0, '../')
#sys.path.insert(0, '.')
from executor import instantiate
from executor import ASSRT
from executor import DBG
#from SchemaParser import ParseSchema
import re
MINBLANKNAMEPARTY='4'

def isSingleNumberERR(StateMap):
 strn=StateMap['line'].strip()
 if strn.isdigit():
	return True
 else:
	return False 

def skip(StateMap):
 handle=StateMap['inputfile']
 handle.readline();

def notrptnotelector(StateMap):
 strn = StateMap['line'].strip()
 #print 'notconstnotret:'+strn
 if strn.find('rptDetailed')==-1 and strn.find('ELECTORS')==-1:
   return True
 else:
   return False



def notconstnotretnotpercentsymb(StateMap):
 strn = StateMap['line'].strip()
 #print 'notconstnotret:'+strn
 if strn.find('Constituency')==-1 and strn.find('rptDetailed')==-1 and strn.find('%')==-1:
   return True
 else:
   return False

 

#    return true if line does not contain 'DETAILED RESULTS'
def isNotDR(StateMap):
 strn = StateMap['line']
 #print 'isNotDR:'+strn
 if strn.find('DETAILED RESULTS')==-1:
   return True
 else:
   return False


def isNotElector(StateMap):
 strn = StateMap['line']
 #print 'isNotElector:'+strn
 if strn.find('ELECTORS')==-1:
   return True
 else:
   return False

#1 KAVETI SAMMAIAH                     M     51        GEN          TRS                47918         60           47978     38.71
def isCandInfo(StateMap):
 #truen true if line starts with integer 
 strn = StateMap['line'].strip()
 #print 'isCandInfo:'+strn
 fstind=strn.find(' ');
 if strn[0:fstind].strip().isdigit() :
   return True 
 else:
   return False


#             1 . RANJIT SINGH                                       M    INC           133018    39.39%
# def isCandInfo(StateMap):
#  #truen true if line starts with integer 
#  strn = StateMap['line'].strip()
#  #print 'isCandInfo:'+strn
#  #first check if this line is the second of the line.. if yes just append the name to candname and return
#  fstind=strn.find('.');
#  if strn[0:fstind].strip().isdigit() :
#    return True 
#  else:
#    return False



# only contains statename hence stripping it is sufficient
def ExtractState(StateMap):
 strn = StateMap['line']
 print 'State name is '+strn
 StateMap['statename']=strn.strip()
 return

#ELECTORS :         212925       VOTERS :   145368     POLL PERCENTAGE :   68.27%   VALID VOTES :   145297
#not being used right now.. ideally we would like to extract this info as well in order to reconcile existing information
def ExtractTotal(StateMap):
 strn = StateMap['line']
 lst=strn.split(':')
 #Incomplete

##########################################################Versions of ExtractPC function depending upon the format%%%%%%%%%%%%%%%%%%%%%%5 
#Constituency :      2 . OUTER MANIPUR (ST)
def ExtractPC(StateMap):
 StateMap['pcname']='';
 StateMap['pctype']='GEN';
 StateMap['pcid']='';
 strn = StateMap['line']
 lst=strn.split(':')
 t=lst[1].strip()
 lstind=t.find('.')
 StateMap['pcid']=t[0:lstind].strip()
 #check if it has a constituency type in bracket..
 m=re.search(r'([\.\w\s-]+)[\(]?([SCT]*)[\)]?[\s]{4,}',t[lstind+1:].strip())
 print t[lstind+1:].strip()
 StateMap['pcname']=m.group(1).strip()
 if len(m.group(2))!=0:
   StateMap['pctype']=m.group(2).strip()
 #print StateMap['statename']+','+StateMap['pcname']+','+StateMap['pctype']
 print StateMap['pcname']+','+StateMap['pctype']
 return

#Constituency       2  OUTER MANIPUR (ST)
#(Constituency)[\s]{2,}([\d]+)[\s]{1,}([\w\s\-\(\)\,\.]+)[\s]{1,}[\(]([\w\s]+)[\)]
def ExtractPC_Without_dot(StateMap):
 StateMap['pcname']='';
 StateMap['pctype']='GEN';
 StateMap['pcid']='';
 strn = StateMap['line'].strip()
 print 'line: '+strn
 #m=re.search(r'(Constituency)[\s]{2,}([\d]+)[\s]{1,}([\w\s\-\(\)\,\.]+)',strn)
 m=re.search(r'(Constituency)[\s]{2,}([\d]+)[\.][\s]{1,}([\w\s\-\(\)\,\.]+)[\s]{2,}(TOTAL ELECTORS :)[\s]{1,}([\d]+)',strn) 
 StateMap['pcid']=m.group(2).strip()
 rest=m.group(3).strip()
 #check if it has a constituency type in bracket..
 #m=re.search(r'([\.\w\s-]+)[\(]?([SCT]*)[\)]?[\s]{4,}',rest)
 m=re.search(r'([\.\w\s-]+)[\(]?([SCT]*)[\)]?',rest)
 print rest
 StateMap['pcname']=m.group(1).strip()
 if len(m.group(2))!=0:
   StateMap['pctype']=m.group(2).strip()
 #print StateMap['statename']+','+StateMap['pcname']+','+StateMap['pctype']
 print StateMap['pcname']+','+StateMap['pctype']
 return
#######################################################################################################################
#Normal case:
#             1 . RISHANG                                              M    SOC            35621    29.85%

def ExtractCandInfo(StateMap,fname):
 strn = StateMap['line']
 #print strn
 #first check if this line is the second of the line.. if yes just append the name to candname and return
 strn=strn.strip()
 fstind=strn.find(' ');
 #fstind=strn.find('.');
 if not strn[0:fstind].strip().isdigit() :
   #ASSRT(False,'Some serious error as candidate info should start from integer')
   StateMap['candname']=StateMap['candname']+' ' + strn.strip()
   #delete last line from some file,, while one??
   ASSRT(StateMap['fileptr']!=0,' Some serious error by this time something must have been assigned there')
   StateMap[fname].seek(StateMap['fileptr'])
   return
   #if typ=='accandfile':
     #StateMap['accandfile'].seek(StateMap['fileptr'])
   #else:
     #ASSRT(typ=='pccandfile', ' Some serious error, as only these two options are allowed for now')
     #StateMap['pccandfile'].seek(StateMap['fileptr'])
   #return
 #else do the normal thing of filling after clearing all stuff
 StateMap['candid']=''
 StateMap['candname']=''
 StateMap['party']=''
 StateMap['candvotes']=''
 StateMap['candid']=strn[0:fstind].strip()
 strn=strn[fstind+1:].strip()
 lstind=strn.rfind(' ')
 strn=strn[0:lstind].strip() #removed percentage part
 lstind=strn.rfind(' ')
 StateMap['candvotes']=strn[lstind+1:].strip()
 strn=strn[0:lstind].strip()
 # , added because of some candidate name in 1989 contained comma
 # @ and \ added because some candidate name in 1996 election contained them
 m=re.search(r'([\s\w\,\.\@\\\(\)\`\'\"]+)[\s]{4,}([MF])[\s]{3,}([\s\w\.\(\)\,\.]+)',strn)
 if m is None:
  m=re.search(r'([\s\w\,\@\\\.\(\)\`\'\"]+)[\s]{1,}([MF])[\s]{2,}([\s\w\.\(\)\,\.]+)',strn)
 if m is None or len(m.groups())!=3:
  #write to error file that complete info not present
  print 'ERR FMT:'+StateMap['line']
  StateMap['candid']='--ERR--'
  StateMap['candname']='--ERR--'
  StateMap['party']='--ERR--'
  StateMap['candvotes']='--ERR--'
 else:
  ASSRT(len(m.groups())==3,'Some error in the format of name sex party')
  StateMap['candname']=m.group(1).strip()
  StateMap['candsex']=m.group(2).strip()
  StateMap['party']=m.group(3).strip()
 # print StateMap['candname']+'               '+StateMap['candsex']+'     '+StateMap['party']
 # print StateMap['party']
 return 


####################################################################################################################
parser=argparse.ArgumentParser()
parser.add_argument('-i','--inp',required=True,help="Input file to parse",type=str)
parser.add_argument('-d','--dot',required=True,help="Input specification automata file in dot format")
#parser.add_argument('-s','--schema',required=True,help="Input schema file containing the schema of all tables needed")
results=parser.parse_args()

tabcoltypeinfo=dict();
tabcolsetinfo=dict();
#print results.inp+','+results.dot + ',' + results.schema
print results.inp+','+results.dot

#ParseSchema(results.schema,tabcoltypeinfo,tabcolsetinfo)
#instantiate(results.dot,results.inp,tabcoltypeinfo,tabcolsetinfo)
instantiate(results.dot,results.inp)
#instantiate('machine.dot','newres.txt')
