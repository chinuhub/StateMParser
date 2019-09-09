import os
import subprocess
import csv

DBG=1
def DBG(strn):
  if DBG==1:
        print strn;
  return

def ASSRT(bchk,msg):
  if bchk!=True:
    print msg
    quit()
  return

#This function returns the integer number of the renamed pdf
def yearBasedRenaming(fname):

 #we mainly do three range checks as following;
 #from 50-99, check if the lename contains something like this 
 #if yes then rename the file as 19+that number .pdf
 #from 0-9 and check if the file name contains something like 0+number
 #if yes then rename the file as 200+that number .pdf
 #from 10-20(depending upon the last year of election), check if the file name contains that number
 #if yes then rename the file as 20+that number .pdf
 for k in range(50,100):
   strk=str(k)
   if strk in fname:
     return int('19'+strk)
 

 for k in range(10,20):
   strk='0'+str(k)
   if strk in fname:
     return int('2'+strk)
#Note: here the order of these two loops matter, why? because 2019 has 01 in it as well
#Note: here forward loop from 0 to 9 is problem why? because 2009 has 00 in it ..
 for k in range(9,-1,-1):
   strk='0'+str(k)
   if strk in fname:
     return int('20'+strk)


 print fname
 ASSRT(False,'Some seriour error in pdf file renaming as no predefined patter of years found in the filename') 
 

 
''' Mapping to denote an election (loksabha number) to years in which that election took place'''
ls_num=dict()
ls_num= {'1':['1962'],
        '2':['1967'],
	'3':['1971'],
	'4':['1977'],
	'5':['1980'],
	'6':['1984','1985'],
	'7':['1989'],
	'8':['1991','1992'],
	'9':['1996']
       }
'''ls_num= {'1':['1962'],
        '2':['1967'],
	'3':['1971'],
	'4':['1977'],
	'5':['1980'],
	'6':['1984','1985'],
	'7':['1989'],
	'8':['1991','1992'],
	'9':['1996']
       }'''

dotfiles=dict()
dotfiles={'Assam':{'1951':'candinfoparser.pc.withoutdot.dot',
                  '1957':'candinfoparser.pc.withoutdot.dot',
                   '1962':'candinfoparser.pc.withoutdot.dot',
                   '1985':'candinfoparser.pc.withoutdot.dot'
                 }
}


'''Mapping to deonte an election (loksabha number) and file name to the automata file which will drive that file's parsing'''
mc_file=dict()
mc_file={'1':[['candinfoparser.dot','candinfoparser_helper_62.py'],['pcinfodetailedparser.dot','pcinfodetailedparser_helper.py']]
	
	}


'''Read set of pdf files present in the current directory'''
'''TODO: later change the directory path to be taken as an input'''

finalf=open('final.csv',"wb+")
finalcsv=csv.writer(finalf)
finalcsv.writerow(['State_name','PC_number','PC_name','PC_type','Candidate_name','Candidate_sex','Party_abbreviation','Votes1','Year'])
#os.walk("../States")
lsd=[x[0] for x in os.walk("../States/")]
lsd=lsd[1:]
print lsd
for dirs in lsd:
  state=os.path.basename(os.path.normpath(dirs))
  print dirs+":"+state
  if ('Assam' not in state) and ('Tamilnadu' not in state):
    continue
  for fls in os.listdir(dirs):
    print fls
    n=yearBasedRenaming(fls)
    year=str(n)
    #print 'file: '+fls+' is renamed as '+str(n)+'.pdf'
    #now invoke command mv to rename the file as str(n).pdf
    cmd="mv \""+dirs+"/"+fls+"\" "+dirs+"/"+year+".pdf"
    #p=subprocess.Popen(cmd, shell=True)   
    #p.wait()
    #now run pdftotxtconvertor
    cmd="pdftotext -layout -nopgbrk "+dirs+"/"+year+".pdf "+year+".txt"
    DBG(cmd)
    p=subprocess.Popen(cmd,shell=True) 
    p.wait()  
    #then cleanedup.txt
    cmd="perl cleanup.pl "+year +".txt " + year+".cleaned"
    DBG(cmd)
    p=subprocess.Popen(cmd, shell=True)   
    p.wait()
    #then invoke candinfo_parser_helper.py function with filename and dotfile as argument, along with state and year
    #first check if statename and year form an exception.. if yes, get their name and then change the path
    dotname='candinfoparser.dot' #name of the default dot file used where exception is not being used.
    if state in dotfiles:
      if year in dotfiles[state]:
        dotname=dotfiles[state][year]
    cmd="python candinfoparser_helper_62.py -i "+ year+".cleaned -d " + dotname +" > r"+year
    DBG(cmd)
    p=subprocess.Popen(cmd, shell=True)   
    p.wait()
    #now read candinfo file as csv and add a column same as year
    v=open('candinfo')
    csr=csv.reader(v)
    for item in csr:
      item.append(year)
      item.append(state)
      finalcsv.writerow(item)
    v.close()
    p=subprocess.Popen("rm *.txt *.cleaned",shell=True)
    p.wait()
  break
finalf.close()


    #copy the content of candinfo to final.csv 
    #remove cleanedup.txt and candinfo files and other intermediate files
 
 

# for elec in ls_num:
#     yearlst= ls_num[elec]
#     for year in yearlst:
#       ASSRT(os.path.exists('../VOL-Ipdfs/'+year+'.pdf'),"File ../VOL-Ipdfs/"+year+".pdf does not exist")

# #now run R script present in the current directory
# cmd="Rscript combine_pdf_xls_candinfo_generator.R" 
# DBG(cmd)
# p=subprocess.Popen(cmd, shell=True)   
# p.wait()
# p=subprocess.Popen("rm candinfo final.csv",shell=True)
# p.wait()
