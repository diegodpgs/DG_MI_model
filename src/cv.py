import os

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

  test_folder = []
  train_folder = []

  size_sentences = len(sentences) 
  size_folder = size_sentences//5

  for index in range(0, len(sentences),size_folder):

    test_folder.append('\n'.join(sentences[index:index+size_folder]))
    train_folder.append('\n'.join(sentences[index+size_folder:]))
    train_folder[-1] += '\n'.join(sentences[0:index])

  return test_folder,train_folder


def getCVFolders(PATH_CONLLU):
  languages_CV = {}

  for language in os.listdir(PATH_CONLLU):
    PATH = '%s/%s' % (PATH_CONLLU,language)

    for arquivo in os.listdir(PATH):
      test, train = CV(getSentences(PATH+'/'+arquivo))
      languages_CV[language] = {'test':test,'train':train}

  return languages_CV