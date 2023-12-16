import os
import shutil

def getSentences(conllu_file):
  sentences = []
  sentence = ''

  for line in open(conllu_file).read().split('\n'):
    if len(line) < 2:
        sentences.append(sentence)
        sentence = ''
    else:
       sentence += line+'\n'
  
  return sentences

def CV(sentences):

  folders_split = ['' for i in range(5)]
  folders = [{'train':'','test':''} for i in range(5)]

 
  for index in range(len(sentences)):
    folders_split[index % 5] += '\n'.join(sentences[index])

  for index in range(5):
    folders[index]['test']  = folders_split[index]
    folders[index]['train'] = ''.join(folders_split[0:index])+''.join(folders_split[index+1:])

  return folders

def getCVFolders(PATH_CONLLU):
  languages_CV = {}

  for language in os.listdir(PATH_CONLLU):
    PATH = '%s/%s' % (PATH_CONLLU,language)

    
    for arquivo in os.listdir(PATH):
        folders = CV(getSentences(PATH+'/'+arquivo))
        languages_CV[language] = {'test':[f['test'] for f in folders],'train':[f['train'] for f in folders]}
  
  return languages_CV


def createFolders(PATH,folders):

  try:
    os.mkdir(PATH)
  except:
    print(PATH,' Already exist. All files within folder will be deleted')
    shutil.rmtree(PATH)
    os.mkdir(PATH)


  for language, data in folders.items():
    os.mkdir('%s/%s' % (PATH,language))
    for index,conllu in enumerate(data['train']):
        file_name_train = '%s__%s__train.conllu' % (language,index)
        writerTR = open('%s/%s/%s' % (PATH,language,file_name_train),'w')
        writerTR.write(conllu)

    for index,conllu in enumerate(data['test']):
        file_name_train = '%s__%s__test.conllu' % (language,index)
        writerTR = open('%s/%s/%s' % (PATH,language,file_name_train),'w')
        writerTR.write(conllu)
  

  # if language not in os.listdir(PATH):
  #   os.mkdir(language)

  # writer_test = open('%s/%s_test_.conllu')
    
if "__main__":
  folders = getCVFolders('/home/diego/ProjectGit/DG_MI_model/data/')  
  createFolders('/home/diego/ProjectGit/DG_MI_model/data_cv/',folders)