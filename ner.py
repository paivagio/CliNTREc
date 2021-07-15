# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 16:43:44 2021

@author: paiva
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 10:03:13 2021

@author: paiva
"""

import sys, re, nltk, stanza, json
import torch
import numpy as np

from progress.bar import IncrementalBar
from transformers import BertTokenizer,BertForTokenClassification
from lxml import etree
from xml.etree import ElementTree as ET
from negex import sortRules, negTagger
from preprocessing import clean2encode, ec_filter, normalize

def generate_XML(resume_text, result_BERT, xml_output, idp, age, sex, cid, birth):
    #tags from BERT
    abbrBERT = {'CH': 'Condition',
                'T':'Procedure_Device',
                'EV':'Observation',
                'G':'Observation',
                'AS':'Anatomic_location',
                'N':'Negation',
                'OBS':'Observation',
                'C':'Condition',
                'R':'Observation',
                'DT':'Temporal_constraints',
                'THER':'Drug_Substance',
                'V':'Measurement',
                'RA':'Route of Administration',
                'O':'O'}
    
    entity_lists=['Condition','Observation','Procedure_Device','Drug_Substance','Route of Administration'
                  ,'Negation']
    attribute_lists=['Measurement','Temporal_constraints','Qualifiers_Modifiers','Anatomic_location']
    
    #concatanate group of words of the same entity type which are close together and expand the abbreviation
    result_BERT_grouped = []
    for sentence in result_BERT:
        sent = []
        s = ''
        n = ''
        flag = 0 #shows if a sentence is beeing built or not (1 yes, 0 no)
        for word in sentence:
            if(word[2] == 'O'):
                if(flag == 0):
                    sent.append((word[0], word[2]))
                else:
                    sent.append((s, abbrBERT[n]))
                    s = ''
                    n = ''
                    flag = 0
                    sent.append((word[0], word[2]))
            else:
                if(word[2][0] == 'B'):
                    if(flag == 0):
                        s = word[0]
                        n = word[2][2:]
                        flag = 1
                    else:
                        sent.append((s, abbrBERT[n]))
                        s = word[0]
                        n = word[2][2:]
                if(word[2][0] == 'I'):
                    if(flag == 0):
                        sent.append((word[0],abbrBERT[word[2][2:]]))
                    else:
                        s+= ' ' + word[0]
        
        result_BERT_grouped.append(sent)    
    
    #Create the xml file    
    text = resume_text
    root = etree.Element("root")
    
    subEl = etree.SubElement(root, 'ID')
    subEl.text = idp
    subEl = etree.SubElement(root, 'AGE')
    subEl.text = age
    subEl = etree.SubElement(root, 'GENDER')
    subEl.text = sex
    subEl = etree.SubElement(root, 'BIRTH')
    subEl.text = birth
    subEl = etree.SubElement(root, 'CID')
    subEl.text = cid
    textxml = etree.SubElement(root, "FREE_TEXT")
    textxml.text = text
    
    for sentence in result_BERT_grouped:
        sent = etree.SubElement(root, "sent")
        i = 1
        textsent = etree.SubElement(sent, "text")
        t = ''
        for word in sentence:
            t+= word[0] + ' '
            if word[1] != 'O':
                if(word[1] in attribute_lists):
                    at = etree.SubElement(sent, "attribute")
                    at.set('class', word[1])
                    at.set('index', 'T'+str(i))
                    i+=1
                    at.set('start', str(text.find(word[0])))
                    at.text = word[0]
                    
                elif(word[1] in entity_lists):
                    ent = etree.SubElement(sent, "entity")
                    ent.set('class', word[1])
                    ent.set('index', 'T'+str(i))
                    i+=1
                    ent.set('negation', 'N')
                    ent.set('relation', 'None')
                    ent.set('start', str(text.find(word[0])))
                    ent.text = word[0]
        textsent.text = t.replace(' . ', '.')
        
        tree = etree.ElementTree(root)
        tree.write(xml_output, pretty_print=True, xml_declaration=True, encoding="utf-8")
    
def run_pos(sentences):
    #https://stanfordnlp.github.io/stanza/pipeline.html
    nlp = stanza.Pipeline('pt', processors='tokenize, pos', logging_level = 'FATAL')
    
    sentences_pos = []
    for sent in sentences:
        doc = nlp(sent)
        sent_pos = []
        for s in doc.sentences:
            for word in s.words:
                sent_pos.append((word.text,word.upos))
        sentences_pos.append(sent_pos) 
    
    return sentences_pos

def predictBERTNER(sentencas,MODEL_DIR):
        
    model = BertForTokenClassification.from_pretrained(MODEL_DIR)
    tokenizer = BertTokenizer.from_pretrained(MODEL_DIR, do_lower_case=True) # lower or not, this is important

    with open(MODEL_DIR + '/idx2tag.json', 'r') as filehandle:
        idx2tag = json.load(filehandle) 
        
    predictedModel=[]
    
    for test_sentence in sentencas:
        tokenized_sentence = tokenizer.encode(test_sentence)
        input_ids = torch.tensor([tokenized_sentence])#.cuda()
        
        with torch.no_grad():
            output = model(input_ids)
        label_indices = np.argmax(output[0].to('cpu').numpy(), axis=2)
        
        # join bpe split tokens
        tokens = tokenizer.convert_ids_to_tokens(input_ids.to('cpu').numpy()[0])
        new_tokens, new_labels = [], []
        for token, label_idx in zip(tokens, label_indices[0]):
            if token.startswith("##"):
                new_tokens[-1] = new_tokens[-1] + token[2:]
            else:
                new_labels.append(label_idx)
                new_tokens.append(token)
            
        FinalLabelSentence = []
        for token, label in zip(new_tokens, new_labels):
            label = idx2tag[str(label)]
            if label == "O" or label == "X":
                FinalLabelSentence.append("O")
            else:
                FinalLabelSentence.append(label)
                
        predictedModel.append(FinalLabelSentence[1:-1]) # delete [SEP] and [CLS]
        
            
    return predictedModel

def run_bert(model_dir, pos):
    
    #the model accepts only lower and no POS is needed
    sentences_lower = []
    for sent in pos:
        temp = []
        for word in sent:
            temp.append(word[0].lower())
        sentences_lower.append(temp)

    #predict
    BERT = predictBERTNER(sentences_lower,model_dir)

    #group (word, pos, ner)
    result_BERT = []
    for index, sentence in enumerate(pos):
        sent = []
        #sentece = [('word', 'pos'), ('word2', 'pos2'),...]
        for i, word in enumerate(sentence):
            #word = ('word', 'pos')
            #word_ner = ('word', 'stz', 'ner')
            word_final = word + (BERT[index][i],)
            sent.append(word_final)
        result_BERT.append(sent)
    
    return result_BERT
   
def split_resume(text):
    info = text.split('\n')
    idp = info[0][4:]
    age = info[1][7:]
    sex = info[2][6:]
    cid = info[3][5:]
    birth = info[4][20:]
    free = info[5][5:]
    
    return idp, age, sex, cid, birth, free

def detect_negation(concept,sent,irules):
        '''
        pattern="^\s?(\w?.*\w?)\s?"
        match=re.search(pattern,concept)
        clean_concept=match.group(1)
        words=re.split("\s+",clean_concept)
        if len(words)>2:
            words=[words[-2],words[-1]]
            concept=" ".join(words)
        '''
        tagger = negTagger(sentence = sent, phrases =[concept], rules = irules, negP=False)
        tag=tagger.getNegationFlag()
        negation = "Y" if tag=="negated" else "N"

        return negation
    
def add_negation(xml_dir):
    NER_tree = ET.ElementTree(file=xml_dir)
    root = NER_tree.getroot()
    with open('models/Negex_input.txt', 'r') as file:
        rules = sortRules(file.readlines())
    for n in root:
        for sent in n:
            sent_text = ''
            for t in sent.findall('text'):
                sent_text = t.text
    
            for ent in sent.findall('entity'):
                if ent.attrib['class']=='Negation':
                    continue
                
                ent.attrib['negation'] = "N"
                concept = ent.text
                neg_tag = detect_negation(concept,sent_text,rules)
                ent.attrib['negation'] = neg_tag

    with open(xml_dir, 'wb') as file:
        NER_tree.write(file)
       
def main(file_name, inp, out):
    input_dir = inp
    text_file = file_name #test.txt'
    output_dir = out

    if(text_file != ''):
        try:
            print("Reading text file from ", input_dir+'/'+text_file)
            with open(input_dir+'/'+text_file, 'r', encoding='UTF-8') as f:
                pacient = f.read()
            idp, age, sex, cid, birth, free_text = split_resume(pacient)
        except:
            print("Error 02!")
            sys.exit(1)
        else:
            print("File successfully opened.\n")
    else:
        print("Error 01!")
        sys.exit(1)

    #Progression bar
    bar = IncrementalBar('Extracting Information', max = 7, suffix='%(percent)d%%')

    #create NER xml file name
    name = re.search('^(.*)\.txt',text_file)
    if name:
        filename = name.group(1)
    output_ner = output_dir+'/'+filename+'_EHR.xml'

    bar.next()

    #split the sentences
    text = free_text.replace(';', '.')
    temp_sents = text.split("\n")
    sents = []
    for sent in temp_sents:
        s = nltk.sent_tokenize(sent, language='portuguese')
        sents.extend(s)

    bar.next()

    #clean and filter EC
    clean_sents = []
    for sent in sents:
        clean_sent = normalize(sent)
        filtered_sent = ec_filter(clean_sent)
        if filtered_sent:
            clean_sents.append(filtered_sent) 

    bar.next()

    #run pos-tagger
    pos = run_pos(clean_sents)

    bar.next()

    #run bert
    bert = run_bert("models/BioBertPtAllClinPt", pos)

    bar.next()

    #generate xml file
    generate_XML(free_text, bert, output_ner, idp, age, sex, cid, birth)

    bar.next()

    #predict negation for entities
    add_negation(output_ner)

    bar.next()

    #extract relations
    
    bar.finish()
    print(f'\nSaving file to {output_ner}')
    return output_ner