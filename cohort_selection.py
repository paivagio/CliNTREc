# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 18:15:26 2021

@author: paiva
"""
import os

from progress.bar import IncrementalBar
from xml.etree import ElementTree as ET
from gensim.models import Word2Vec

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file
  
def areSimilar(text1, text2, w2v, vocab):
    if text1 not in vocab or text2 not in vocab:
        return False
    
    similarity = w2v.wv.similarity(text1, text2)
    if similarity > 0.66:
        return True
    else:
        return False            

def countPositives(dic):
    cohort = []
    num = 0
    for t in dic:
        if t[1] > 0:
            num+=1
            cohort.append(t[0])
    print(f'\nYour clinical trial has {num} elegible pacients!\n')
    return cohort

def findMyPacients(dirEc, dirPacients):
    tags = ['CONDITIONS','OBSERVATIONS','PROCEDURES_DEVICES','DRUGS_SUBSTANCES', 'CONCEPTS']
    tags2 = ['Condition', 'Observation', 'Procedure_Device', 'Drug_Substance', 'Concept']
    skip = ['ID', 'AGE', 'GENDER']
    
    w2v_model = Word2Vec.load("models/Word2Vec/word2vec_model.model")
    vocab = w2v_model.wv.vocab
    
    candidates = {}
    ec = ET.ElementTree(file= dirEc) 
    ecRoot = ec.getroot()
    idEc = ecRoot.find('ID').text
    gender = ecRoot.find('GENDER').text
    
    count = 0
    for f in files(dirPacients):
        count+=1
    
    print(f'Found {count} pacients\n')
    
    #Progression bar
    bar = IncrementalBar('Cohort Selection', max = count, suffix='%(percent)d%%')
    
    for filename in bar.iter(files(dirPacients)):
        score = 0
        pacient = ET.ElementTree(file=dirPacients+filename)                   
        rootP = pacient.getroot() 
        idP = rootP.find('ID').text
        
        
        if gender != 'any':
            if  gender != rootP.find('AGE').text:
                score-=20
            else:
                score+=20
        
        modifier = 1
        for crit in ecRoot:
            if crit.tag in skip:
                continue
            for tag, tag2 in zip(tags, tags2):
                for ent in crit.find(tag).findall(tag2):
                    textEc = ent.text.lower()
                    match = False
                    negated = False
                    mea_match = 0
                    
                    for ent2 in rootP.find(tag).findall(tag2):
                        textEnt = ent2.text.lower()
                        if textEnt == textEc or areSimilar(textEnt, textEc, w2v_model, vocab):
                            match = not match
                            if ent2.attrib['negated'] == 'Y':
                                negated = not negated
                                
                            fields = ['value', 'time', 'place']
                            for f in fields:
                                tEc = ent.attrib[f].split('|')
                                tP = ent2.attrib[f].split('|')
                                for t1 in tEc:
                                    for t2 in tP:
                                        if t1=='' or t2=='':
                                            continue
                                        if t1 == t2:
                                            mea_match+=0.5
                                        else:
                                            mea_match-=0.5
                            
                    if match and not negated:
                        score+= 5*modifier+mea_match
                    else:
                        pass
                        #score+= -1*modifier     
            modifier = -1
        candidates[idP] = score
        
    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    cohort = countPositives(sorted_candidates)
    filename = re.sub('(\.xml)|(\_structured\.xml)', '', dirEc.split('/')[-1])
    with open ('temp/'+filename+'_pacients.txt', 'w') as file:
        for selected in cohort:
            file.write(selected+'\n')

def countPositivesP(dic):
    num = 0
    for t in dic:
        if t[1] > 0:
            num+=1
    print(f'Your pacient is elegible for {num} trials!')
    return num

def findMyTrials(dirP, dirEcs):
    tags = ['CONDITIONS','OBSERVATIONS','PROCEDURES_DEVICES','DRUGS_SUBSTANCES', 'CONCEPTS']
    tags2 = ['Condition', 'Observation', 'Procedure_Device', 'Drug_Substance', 'Concept']
    w2v_model = Word2Vec.load("models/Word2Vec/word2vec_model.model")
    vocab = w2v_model.wv.vocab
    
    pacient = ET.ElementTree(file=dirP)                   
    rootP = pacient.getroot() 
    idP = rootP.find('ID').text
    
    candidates = {}
    for filename in files(dirEcs):
        ec = ET.ElementTree(file= dirEcs+filename) 
        ecRoot = ec.getroot()
        idEc = ecRoot.find('ID').text
        score = 0
        modifier = 1
        for crit in ecRoot:
            if crit.tag == 'ID':
                continue
            for tag, tag2 in zip(tags, tags2):
                for ent in crit.find(tag).findall(tag2):
                    textEc = ent.text.lower()
                    match = False
                    negated = False
                    mea_match = 0
                    
                    for ent2 in rootP.find(tag).findall(tag2):
                        textEnt = ent2.text.lower()
                        if textEnt == textEc or areSimilar(textEnt, textEc, w2v_model, vocab):
                            match = not match
                            if ent2.attrib['negated'] == 'Y':
                                negated = not negated
                                
                            fields = ['value', 'time', 'place']
                            for f in fields:
                                tEc = ent.attrib[f].split('|')
                                tP = ent2.attrib[f].split('|')
                                for t1 in tEc:
                                    for t2 in tP:
                                        if t1 == t2:
                                            mea_match+=0.5
                                        else:
                                            mea_match-=0.5
                                            
                    if match and not negated:
                        score+= 5*modifier+mea_match
                    else:
                        score+= -1*modifier     
            modifier = -1
        candidates[idEc] = score
        
    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    countPositivesP(sorted_candidates)