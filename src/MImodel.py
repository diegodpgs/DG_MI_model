from collections import defaultdict
from collections import Counter
import numpy as np
import os
import time
import random

class MImodel:

  def __init__(self,PATH,sentence_length):
    self.PATH = PATH
    self.mult_dists_x = {}
    self.mult_dists_yx = {}
    self.matchs_DDA = {}
    self.matchs_UDA = {}
    self.total_compared_relation = {}
    self.syntatic_relations_testset = {}
    self.smoothing = 'null'
    self.deprel = ['nsubj','obj','iobj','csubj','ccomp','xcomp','obl','vocative','expl','dislocated','advcl','advmod','discourse','aux','cop','mark','nmod','appos','nummod','acl','amod','det','clf','case','conj','cc','fixed','flat','compound','list','parataxis','orphan','goeswith','reparandum','punct','root','dep']
    self.__content__ = 'FORM'
    self.sentence_length = sentence_length
    self.__initVariables()

  def parseConllu(self,data_CONLLU):
    conllu_parsed = []
    es = 0
    
    sentence = []
    
    for line in data_CONLLU:

        if self.__end_sentence__(line):
          conllu_parsed.append((self.getSentenceDepRelations(sentence),sentence))
          sentence = []
          es += 1

        elif self.__is_validconst__(line):
          sentence.append(self.parseLine(line))

    return {'depRel':[lp[0] for lp in conllu_parsed],'sentence':[lp[1] for lp in conllu_parsed]}

  def getSentenceDepRelations(self,sentence):
    deprel = []
    ids = dict([(const['ID'],const[self.__content__]) for const in sentence])
    idspos = dict([(const['ID'],const['UPOS']) for const in sentence])


    for line in sentence:
      if ':' in line['DEPREL']:
        line['DEPREL'] = line['DEPREL'].split(':')[0]

      if line['HEAD'] == '0':
        deprel.append({'HEAD':'root',
                       'DEP':line[self.__content__],
                       'DEPREL':line['DEPREL'],
                       'UPOSD':line['UPOS'],
                       'UPOSH':line['UPOS'],
                       'distance_dep_relation':line['distance_dep_relation']})
      else:
        deprel.append({'HEAD':ids[line['HEAD']],
                       'DEP':line[self.__content__],
                       'UPOSD':line['UPOS'],
                       'UPOSH':idspos[line['HEAD']],
                       'DEPREL':line['DEPREL'],
                       'distance_dep_relation':line['distance_dep_relation']})


    return deprel


            
  
  def __initVariables(self):

    
      self.matchs_DDA = dict([(dp,0) for dp in self.deprel])
      self.matchs_UDA = dict([(dp,0) for dp in self.deprel])
      self.total_compared_relation = 0

  def __smoothing(self,token_frequency,total_tokens_frequency):

    if self.smoothing == 'null':
      return token_frequency

    if self.smoothing == 'laplace':

      if token_frequency != 0:
        return token_frequency

      return 1/total_tokens_frequency

  def computeMI(self,language,x,y):
    """For reference: https://people.cs.umass.edu/~elm/Teaching/Docs/mutInf.pdf
       For white house
       y = freq(white)
       x = freq(house)
    """

    IM = 0
    totalfreq = float(np.sum(list(self.mult_dists_yx.values())))
    distx = self.__smoothing(self.mult_dists_x[x],totalfreq)
    disty = self.__smoothing(self.mult_dists_x[y],totalfreq)
    distyx = self.__smoothing(self.mult_dists_yx['%s<#>%s' % (y,x)],totalfreq)

    
    if distyx == 0:
        return 0
    join = distyx/totalfreq

    return join*(np.log2(distyx)+np.log2(totalfreq)-np.log2(distx)-np.log2(disty))

  def __end_sentence__(self,line):
    return True if len(line) == 0 else False

  def __is_validconst__(self,line):
    idtoken = line.split()[0]

    return True if idtoken[0].isdigit() and ('.' not in idtoken and '-' not in idtoken) else False

  def computeDist(self,CONLLU_file):

      dist_x = defaultdict(int)
      dist_yx = defaultdict(int)
      index = 0
      previous_token = ''
      previous_lema = ''

      while index < len(CONLLU_file):
       
        if self.__end_sentence__(CONLLU_file[index]):
          previous_token = ''
          previous_lema = ''
        elif self.__is_validconst__(CONLLU_file[index]):


          token = CONLLU_file[index].split('\t')[1]
          dist_x[token] += 1


          if previous_token != '':
            dist_yx['%s<#>%s' % (previous_token,token)] += 1

          previous_token = token


        index += 1

      return dist_x, dist_yx


  def parseLine(self,const):
    """We used the same terms described in https://universaldependencies.org/format.html at 26 September 2023"""

    field = const.split('\t')
    distance = abs(int(field[0])-int(field[6]))



    return {'distance_dep_relation':distance,
            'ID':field[0],
            'FORM':field[1],
            'lema_pos':'%s_%s' % (field[2],field[3]),
            'LEMMA':field[2],
            'UPOS':field[3],
            'XPOS':field[4],
            'FEATS':field[5],
            'HEAD':field[6],
            'DEPREL':field[7]}



  def combination(self,language, sentence,distance_limit):

    list_combinations = []
    for index_c1, const1 in enumerate(sentence):

      for index_c2 in range(index_c1,len(sentence)):
        if index_c1 == index_c2:
          continue

        if index_c2 - index_c1 <= distance_limit:
          const1_form = const1[self.__content__].replace('--','-')
          const2_form = sentence[index_c2][self.__content__].replace('--','-')

          list_combinations.append((self.computeMI(language,const1[self.__content__],sentence[index_c2][self.__content__]),const1_form,const2_form))
          

    list_combinations = list(set(list_combinations)) #Remove duplicates
    list_combinations.sort()

    return list_combinations[::-1]

 

  def __processPairs(self,relations,permutation_pairs,language,max_distance_relations,log=False):

    if len(relations) == 0:
        return
    relations_pairs = []


    for r in relations:

      relations_pairs.append('%s<#>%s' % (r['HEAD'],r['DEP']))

      if r['DEPREL'] not in self.syntatic_relations_testset:
        self.syntatic_relations_testset[r['DEPREL']] = 0


      self.syntatic_relations_testset[r['DEPREL']] += 1

    relations_pairs_buffer = relations_pairs.copy()

    for index_pair,perm_pair in enumerate(permutation_pairs):
      A = len(perm_pair[1])
      B = len(perm_pair[2])

      #if A > B :#and self.mult_dists_x[perm_pair[1]] > self.mult_dists_x[perm_pair[2]]:
      #  perm_pair_hd  = '%s<#>%s' % (perm_pair[1],perm_pair[2])
      #  perm_pair_dh  = '%s<#>%s' % (perm_pair[2],perm_pair[1])
      #else:
      perm_pair_hd  = '%s<#>%s' % (perm_pair[2],perm_pair[1])
      perm_pair_dh  = '%s<#>%s' % (perm_pair[1],perm_pair[2])



      self.total_compared_relation += 1

      if perm_pair_hd in relations_pairs_buffer:
        index_relation = relations_pairs.index(perm_pair_hd)
        
          
        self.matchs_UDA[relations[index_relation]['DEPREL']] += 1
        self.matchs_DDA[relations[index_relation]['DEPREL']] += 1

        while perm_pair_hd in relations_pairs_buffer:
          relations_pairs_buffer.remove(perm_pair_hd) #To avoid compare to the same relation

      elif perm_pair_dh in relations_pairs_buffer:
        index_relation = relations_pairs.index(perm_pair_dh)

        self.matchs_UDA[relations[index_relation]['DEPREL']] += 1

        while perm_pair_dh in relations_pairs_buffer:
          relations_pairs_buffer.remove(perm_pair_dh) #To avoid compare to the same relation


  def train(self,data_train,smoothing='null'):
    self.smoothing = smoothing
    

    dists = self.computeDist(data_train)
    self.mult_dists_x = dists[0]
    self.mult_dists_yx = dists[1]

  def testExp(self,data_test,language,max_distance_relations,max_length_sentence):
    parsed = self.parseConllu(data_test)
   
    #{'depRel':[lp[0] for lp in conllu_parsed],'sentence':[lp[1] for lp in conllu_parsed]}

    total_sentences = len(parsed['sentence'])
    permutation_count = 0
    previous_precision = 0
    sentences_processed = 0

    self.syntatic_relations_testset = {}

    for index_sentence, sentence in enumerate(parsed['sentence']):

      if len(sentence) > max_length_sentence:
        continue

      #sf = self.__get_sentence_form(sentence).split()
      startp = time.time()

      #if index_sentence % 200 == 0:
      #  print('%.1f%% sentences processed ' % ((index_sentence/len(parsed['sentence']))*100))


      p = self.combination(language,sentence,max_distance_relations)


      if len(p) > 0:

        relations = parsed['depRel'][index_sentence]

        relations_pair_function = [r['DEPREL'] for r in relations]

        self.__processPairs(relations,p[0:len(relations)],language,max_distance_relations)

    if sum(self.syntatic_relations_testset.values()) == 0:
      return 0,0
    UDA = sum(self.matchs_UDA.values())/sum(self.syntatic_relations_testset.values())
    DDA = sum(self.matchs_DDA.values())/sum(self.syntatic_relations_testset.values())

    return UDA,DDA


           