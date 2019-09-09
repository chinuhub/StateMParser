import pydot
#import pyparsing
import json
import re
import sys


DBG=0

def DBG(strn):
  if DBG==1:
	print strn;
  return

def ASSRT(bchk,msg):
  if bchk!=True:
    print msg
    quit()
  return

#####################################################################################################
#returns a pair of nextstate, edge outgoing from this state..
def GetOutTransitions(state,graph):
  res=set()
  edgelist= graph.get_edges()   
  for e in edgelist:
	if e.get_source()==state:
 		tu=(e.get_destination(),e.get_attributes()['label'])
		DBG('DBG:GetOutTransition: transition from  '+ state+' to '+(tu[0])+' on label ' + (tu[1]))
		res.add(tu)
  return res 

######################################################################################################
def GetConditionActionPair(edgelabl):
  #parse edge label on | to get condition and action separtely.
  labl=edgelabl[1:-1]
  lst=[x.strip() for x in labl.split('|')]
  #print lst[0]+" and "+lst[1]
  ASSRT(len(lst)==2,'Some serious error as the syntax of edge label is condition|action')
  tup=(lst[0],lst[1])
  return tup


########################################################################################################
def Satisfy(command,GState):
  #check if command is of type contains.. This is to start with..
  m=re.search(r'(contains)\(\'([\(\)\.\%\w\s-]+)\'\)',command)
  if m!=None:
     DBG('DBG:Satisfy: checking if last read line contains '+m.group(2))
     return GState['line'].find(m.group(2))!=-1 #means it will return true if text is found..
  else:
  	m=re.search(r'([\w]+)\((.*)\)',command)
	ASSRT(m!=None,' Some serious error as command is not being parsed properly')	
	#extract its all parameters by splitting m.group(2) on ,
	#assert that no parameter is being passed (for now) and simply invoke the command using reflection.
	ASSRT(len(m.group(2))==0," Only 0 argument commands are supported for condition check except the inbuilt command contains")
	DBG('DBG:Act: About to execute the command ' + m.group(1))
	#for this version we do not handle this, by default just return true.
        if m.group(1).strip()=='true':
         return True
        else:
	 ftocall = getattr(sys.modules['__main__'],m.group(1))
         return ftocall(GState)
# as a result.. any 0 argument function just returns true
#	return ftocall(GState)
     
  
#########################################################################################################
#def Act(commands,GState,tabcoltypeinfo,tabcolsetinfo):
def Act(commands,GState):
  #break the command in individual commands by splitting on ;
  commandlst=[x.strip() for x in commands.split(':')]
  for cmd in commandlst:
	#extract the naem of the command 
  	m=re.search(r'([\w]+)\((.*)\)',cmd)
	ASSRT(m!=None,' Some serious error as command is not being parsed properly')	
	#extract its all parameters by splitting m.group(2) on ,
 	paramlst=[]
	if len(m.group(2))!=0 :
		paramlst=[x.strip() for x in m.group(2).split(',')]
	#if command iswritetofile then handle differently
	GState['statename']="WestBengal"
	if m.group(1)=='Write' :
		ASSRT(len(paramlst)!=0," At least one argument should be provided with this command")
		#paramlst[0] is filename, and other parameters are labels from GState which must be written to filename
		#using , separated entries
		handle=GState[paramlst[0]]
		toput=''
		for ent in paramlst[1:] :
			ASSRT(len(GState[ent])!=0,"Some serious error as label "+ent+" was not set yet")
			if len(toput)==0:
				toput=toput+'\"'+GState[ent]+'\"'
			else:
				ASSRT(ent in GState, ent+' not in global state, some serious error')
				#ASSRT(ent in tabcolsetinfo[handle], ent +' is not a column of table '+ handle +' in schema file')
				#ASSRT(TypeMatch(GState[ent],tabcoltypeinfo[handle]['type']),' Type mismatch found in ' + ent)
				toput=toput+',\"'+GState[ent]+'\"'
		GState['fileptr']=handle.tell()
		handle.writelines(toput+'\n')
	elif m.group(1)=='nop':
           i=1
	#do nothing		
	else :
	#else assert that no parameter is being passed (for now) and simply invoke the command using reflection.
		ASSRT(len(paramlst)<=1," Only 1 argument action commands are supported for now except write file command")
		DBG('DBG:Act: About to execute the command ' + m.group(1))
		ftocall = getattr(sys.modules['__main__'],m.group(1))
		if len(paramlst)==1 :
			ftocall(GState,paramlst[0])
		else:
			ftocall(GState)
  #one argument is being needed sometime like in AC-PC segment handling to check if it is a accandinfo or pccandinfo
			
  return
  

########################################################################################################
#def StartExecution(state,inputfile,GState,graph,tabcoltypeinfo,tabcolsetinfo):
def StartExecution(state,inputfile,GState,graph):
   #put state in a set worklist
   workset=set()
   workset.add(state.get_name())
   #while worklist not empty
   while len(workset)!=0:
      #remove from the worklst
      elem = workset.pop()
      #get outtransitions from this state..
      outtrans=GetOutTransitions(elem,graph)
      #read next line from input file
      #first store the current handle so that we can simulate
      #the effect of rollback of read line.. as it might be
      #needed by some action
      GState['inputptr']=inputfile.tell()
      line=inputfile.readline().strip('\n')
      if len(line)==0:
	break;#means we are done with reading the file
      DBG('DBG:Readline: next line read is '+line)
      GState['line']=line
      #for each out transition
	#get condition, action pair from the edge
	#check if next line satisfies condition
        #if yes take action and put the destination state in worklist
           #break
	#else 
	   #continue
      done=False
      for  edgest in outtrans:
	condactpair=GetConditionActionPair(edgest[1])#edgest is a tuple of <nextstate, transition label connecting them>
	if Satisfy(condactpair[0],GState):
		done=True
		#Act(condactpair[1],GState,tabcoltypeinfo,tabcolsetinfo)#use and fill GState map object by applying action on the line
		Act(condactpair[1],GState)#use and fill GState map object by applying action on the line
		workset.add(edgest[0])
		break
	#endif
      #endfor
      if done==False:
	ASSRT(False,'No transition satisfied by current line from state '+elem +' and readline is ' + line)
   #end while
   if len(inputfile.readline())!=0:
	print 'SOme error as by this time inputfile handle must be empty';
   #file must be empty..   
   return

#########################################################################################################

#def instantiate (dotfile,processfile,tabcoltypeinfo,tabcolsetinfo):
def instantiate (dotfile,processfile):
 	gstate=dict()
	init=""
	graph = pydot.graph_from_dot_file(dotfile)
	fname = open(processfile)
	nodelist = graph.get_node_list()
	statestr=graph.get_attributes()['states']
	#split statelst by : and insert them one by one in gstate map.
	statelst=[x.strip() for x in statestr.split(':')]
	print statelst
	for el in statelst:
		gstate[el]=''
	filestr=graph.get_attributes()['files']
        filestr=filestr[1:-1]
	filelst=[x.strip() for x in filestr.split(':')]
	print filelst
	for el in filelst:
		print 'opened '+el+' for writing'
		#ASSRT(el in tabcoltypeinfo,el+' is not a valid table name (By default table name will be same as the file name)')
		gstate[el]=open(el,'w')
	for n in nodelist:
		if n.get_name()=="\"0\"":
		  init=n;
	gstate['fileptr']=0
        gstate['inputfile']=fname
	#StartExecution(init,fname,gstate,graph,tabcoltypeinfo,tabcolsetinfo)
	StartExecution(init,fname,gstate,graph)
	for el in filelst:
		gstate[el].close()
	return


##########################################################################################################################
def RollBack(StateMap):
   StateMap['inputptr'].seek(StateMap['inputptr']) 
