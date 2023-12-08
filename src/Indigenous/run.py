from MImodel import *
import os
from cv import *
import argparse

def getFileName(language,arguments):

    saida = '%s__%d__%d__%s.txt' % (language,arguments['max_d_r'],arguments['max_s'],arguments['smoothing'])
    return saida

def runExperiments(PATH,language,data_train,data_test,smoothing,max_d_r,max_s):
  arguments = {'PATH':PATH,
               'smoothing':smoothing,
               'max_d_r':max_d_r,
               'max_s':max_s}

  MM = MImodel(PATH,max_s)
  MM.train(data_train,smoothing)

  
  start = time.time()
  folder = '%d_%d' % (max_d_r,max_s)

  if folder not in os.listdir(os.getcwd()):
    os.mkdir(folder)

  #file_ = open(folder+'/'+getFileName(language,arguments),'w')


  return MM.testExp(data_test,language,arguments['max_d_r'],arguments['max_s'])




parser = argparse.ArgumentParser(description='Indigenous languages')
parser.add_argument('--PATH',default='/home', type=str,help="CONLLU files PATH")
parser.add_argument('--max_d_r',default='2',type=str,help='permutation distance between two tokens. Use , to separated different values')
parser.add_argument('--max_s',default='40',type=str,help='The maximum sentence length. Use , to separated different values')
args = parser.parse_args()




languagesCV = getCVFolders(args.PATH)
for max_s in [int(i) for i in args.max_s.split(',')]:
  max_d_r_list = [int(i) for i in args.max_d_r.split(',')]
  max_d_r_list.append(max_s)

  for max_d_r in max_d_r_list:
    for language, data in languagesCV.items():
      train_folder, test_folder = data['train'],data['test']
      ddas = []
      udas = []
           
      for index in range(len(train_folder)):
            UDA, DDA = runExperiments('/content/data',language,train_folder[index].split('\n'),test_folder[index].split('\n'),'laplace',max_d_r,max_s)
            if UDA != 0:
              ddas.append(DDA)
              udas.append(UDA)
      print('%s;%.5f;%.5f;%d;%d' % (language,np.average(udas),np.average(ddas),max_s,max_d_r))