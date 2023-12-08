import MImodel
import cv

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

if "__main__":
  languagesCV = getCVFolders()
  for max_s in [10,40]:
      for max_d_r in [1,2,3,4,5,max_s]:
          #print('Executando %d %d' % (max_s,max_d_r))
          for language, data in languages_CV.items():
            train_folder, test_folder = data['train'],data['test']
            ddas = []
            udas = []
            #print('Processing %s' % language)
            #print('TRAIN %d  TEST %d' % (len(train_folder[0]), len(test_folder[0])))
            
            for index in range(len(train_folder)):
                  UDA, DDA = runExperiments('/content/data',language,train_folder[index].split('\n'),test_folder[index].split('\n'),'laplace',max_d_r,max_s)
                  if UDA != 0:
                    ddas.append(DDA)
                    udas.append(UDA)
            print('%s;%.5f;%.5f;%d;%d' % (language,np.average(udas),np.average(ddas),max_s,max_d_r))