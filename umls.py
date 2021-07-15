# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 16:42:43 2021

@author: paiva
"""
import glob
import sys, os
import re
import vaex
import requests

from progress.bar import IncrementalBar
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords as SW
from xml.etree import ElementTree as ET
from lxml import etree
from negex import sortRules, negTagger
from preprocessing import clean2encode, ec_filter, normalize


                # TUI       LABEL
sty2ellie =    {'T001':'Drug_Substance',#Organism
                'T002':'O',#Plant
                'T004':'Drug_Substance',#Fungus
                'T005':'Drug_Substance',#Virus
                'T007':'Drug_Substance',#Bacterium
                'T008':'O',#Animal
                'T010':'O',#Vertebrate
                'T011':'O',#Amphibian
                'T012':'O',#Bird
                'T013':'O',#Fish
                'T014':'O',#Reptile
                'T015':'O',#Mammal
                'T016':'O',#Human
                'T017':'O',#Anatomical Structure
                'T018':'Anatomic_Location',#Embryonic Structure
                'T019':'Condition',#Congenital Abnormality
                'T020':'Condition',#Acquired Abnormality
                'T021':'Condition',#Fully Formed Anatomical Structure
                'T022':'Anatomic_Location',#Body System
                'T023':'Anatomic_Location',#"Body Part, Organ, or Organ Component"
                'T024':'Anatomic_Location',#Tissue
                'T025':'Anatomic_Location',#Cell
                'T026':'Anatomic_Location',#Cell Component
                'T028':'Condition',#Gene or Genome
                'T029':'Anatomic_Location',#Body Location or Region
                'T030':'Anatomic_Location',#Body Space or Junction
                'T031':'Drug_Substance',#Body Substance
                'T032':'Observation',#Organism Attribute
                'T033':'Condition',#Finding
                'T034':'Observation',#Laboratory or Test Result
                'T037':'Condition',#Injury or Poisoning
                'T038':'O',#Biologic Function                           (lisogenia, homeostase)
                'T039':'O',#Physiologic Function
                'T040':'O',#Organism Function                           (anaerobiose)
                'T041':'O',#Mental Process
                'T042':'O',#Organ or Tissue Function
                'T043':'O',#Cell Function
                'T044':'O',#Molecular Function
                'T045':'O',#Genetic Function
                'T046':'O',#Pathologic Function
                'T047':'Condition',#Disease or Syndrome
                'T048':'Condition',#Mental or Behavioral Dysfunction
                'T049':'Condition',#Cell or Molecular Dysfunction
                'T050':'Condition',#Experimental Model of Disease                       (sarcoma aviário)
                'T051':'O',#Event                                     (acidente aéreo)
                'T052':'O',#Activity                                  (bem-estar do animal, guerra biologica)
                'T053':'O',#Behavior                                   (comportamento mensageiro)
                'T054':'O',#Social Behavior
                'T055':'O',#Individual Behavior
                'T056':'O',#Daily or Recreational Activity               (condução de veículo, basquetebol)
                'T057':'O',#Occupational Activity                         (administração de empresas)
                'T058':'O',#Health Care Activity                        (assistência ambulatorial)
                'T059':'Procedure_Device',#Laboratory Procedure
                'T060':'Procedure_Device',#Diagnostic Procedure
                'T061':'Procedure_Device',#Therapeutic or Preventive Procedure
                'T062':'O',#Research Activity                            (alternativas aos testes com animais)
                'T063':'Procedure_Device',#Molecular Biology Research Technique
                'T064':'O',#Governmental or Regulatory Activity
                'T065':'O',#Educational Activity
                'T066':'O',#Machine Activity                           (gráficos por computador)
                'T067':'Procedure_Device',#Phenomenon or Process
                'T068':'Procedure_Device',#Human-caused Phenomenon or Process
                'T069':'O',#Environmental Effect of Humans            (fluoretação da água)
                'T070':'O',#Natural Phenomenon or Process             (adaptação biológica)
                'T071':'O',#Entity                                    (doações financeiras)
                'T072':'Procedure_Device',#Physical Object
                'T073':'Procedure_Device',#Manufactured Object
                'T074':'Procedure_Device',#Medical Device
                'T075':'Procedure_Device',#Research Device
                'T077':'O',#Conceptual Entity                        (teoria do caos)
                'T078':'O',#Idea or Concept                           (direitos dos animais)
                'T079':'Temporal_constraint',#Temporal Concept
                'T080':'Qualifier_Modifier',#Qualitative Concept
                'T081':'Measurement',#Quantitative Concept
                'T082':'O',#Spatial Concept                    (ligação de carbo-hidratos, meio ambiente)
                'T083':'O',#Geographic Area                     (áfrica)
                'T085':'Drug_Substance',#Molecular Sequence
                'T086':'Drug_Substance',#Nucleotide Sequence
                'T087':'Drug_Substance',#Amino Acid Sequence
                'T088':'Drug_Substance',#Carbohydrate Sequence
                'T089':'O',#Regulation or Law
                'T090':'O',#Occupation or Discipline
                'T091':'O',#Biomedical Occupation or Discipline
                'T092':'O',#Organization
                'T093':'O',#Health Care Related Organization
                'T094':'O',#Professional Society
                'T095':'O',#Self-help or Relief Organization
                'T096':'O',#Group
                'T097':'O',#Professional or Occupational Group
                'T098':'O',#Population Group
                'T099':'O',#Family Group
                'T100':'Temporal_constraint',#Age Group
                'T101':'O',#Patient or Disabled Group
                'T102':'O',#Group Attribute
                'T103':'Drug_Substance',#Chemical
                'T104':'Drug_Substance',#Chemical Viewed Structurally
                'T109':'Drug_Substance',#Organic Chemical
                'T114':'Drug_Substance',#"Nucleic Acid, Nucleoside, or Nucleotide"
                'T116':'Drug_Substance',#"Amino Acid, Peptide, or Protein"
                'T120':'Drug_Substance',#Chemical Viewed Functionally
                'T121':'Drug_Substance',#Pharmacologic Substance
                'T122':'Drug_Substance',#Biomedical or Dental Material
                'T123':'Drug_Substance',#Biologically Active Substance
                'T125':'Observation',#Hormone
                'T126':'Observation',#Enzyme
                'T127':'Observation',#Vitamin
                'T129':'Drug_Substance',#Immunologic Factor
                'T130':'Observation',#"Indicator, Reagent, or Diagnostic Aid"
                'T131':'Drug_Substance',#Hazardous or Poisonous Substance
                'T167':'Drug_Substance',#Substance
                'T168':'Drug_Substance',#Food
                'T169':'Procedure_Device',#Functional Concept          (administração sublingual)
                'T170':'O',#Intellectual Product
                'T171':'O',#Language
                'T184':'Condition',#Sign or Symptom
                'T185':'O',#Classification
                'T190':'Condition',#Anatomical Abnormality
                'T191':'Condition',#Neoplastic Process
                'T192':'Observation',#Receptor                            (receptores adrenérgicos alfa 1)
                'T194':'Drug_Substance',#Archaeon                                  (halobacteriaceae)
                'T195':'Drug_Substance',#Antibiotic
                'T196':'Drug_Substance',#"Element, Ion, or Isotope"                  (alumínio)
                'T197':'Drug_Substance',#Inorganic Chemical
                'T200':'Drug_Substance',#Clinical Drug
                'T201':'Observation',#Clinical Attribute
                'T203':'O',#Drug Delivery Device
                'T204':'Drug_Substance'#Eukaryote                         (aedes, acanthamoeba)
                }

operators = ['maior que','menor que','maior igual a','menor igual a','igual a','igual ou superior a', 'primeiras',
             'acima de', 'abaixo de', 'pelo menos', 'no mínimo', 'no máximo', 'mais de', 'menos de', 'até', 'superior a',
             'inferior a', 'igual ou inferior', 'últimos', 'maior ou igual a', 'menor ou igual a', 'ao menos',
             'maior do que', 'menor do que', 'mais alta que', 'mais baixa que']

triggers = ['mm', 'cm', 'dm', 'm', 'dam', 'hm', 'km', 'ms', 's',
            'min', 'h', 'hs', 'mg', 'ng', 'g', 'kg', 'ml', 'l',
            'anos', 'ano', 'mês', 'mes', 'meses', 'dia', 'dias',
            'mol', 'nmol', 'mmol', 'umol']

def generate_XML(trial_text, result_BERT, xml_output, turn):
    entity_lists=['Condition','Observation','Procedure_Device','Drug_Substance','Route of Administration'
                  ,'Negation', 'Concept']
    attribute_lists=['Measurement','Temporal_constraint','Qualifier_Modifier','Anatomic_Location']
    
    #concatanate group of words of the same entity type which are close together and expand the abbreviation
    result_BERT_grouped = []
    for sentence in result_BERT:
        sent = []
        s = ''
        n = ''  
        r = ''
        a = ''
        flag = 0 #shows if a sentence is beeing built or not (1 yes, 0 no)
        for word in sentence:
            if(word[1] == 'O'):
                if(flag == 0):
                    sent.append((word[0], word[1], word[2], word[3]))
                else:
                    sent.append((s, n, r, a))
                    s = ''
                    n = ''
                    r = ''
                    a = ''
                    flag = 0
                    sent.append((word[0], word[1], word[2], word[3]))
            else:
                if(word[1][0] == 'B'):
                    if(flag == 0):
                        s = word[0]
                        n = word[1][2:]
                        r = word[2]
                        a = word[3]
                        flag = 1
                    else:
                        sent.append((s, n, r, a))
                        s = word[0]
                        n = word[1][2:]
                        r = word[2]
                        a = word[3]
                if(word[1][0] == 'I'):
                    if(flag == 0):
                        sent.append((word[0],word[1][2:], word[2], word[3]))
                    else:
                        s+= ' ' + word[0]
        
        result_BERT_grouped.append(sent)
    
    #Create the xml file    
    text = trial_text
    root = etree.Element("root")
    
    label = "Inclusion" if turn==0 else "Exclusion"
    subroot = etree.SubElement(root, label)
    textxml = etree.SubElement(subroot, "text")
    textxml.text = text
    
    for sentence in result_BERT_grouped:
        sent = etree.SubElement(subroot, "sent")
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
                    at.set('temp', word[2])
                    at.set('pos_rel', word[3])
                    at.text = word[0]
                    
                elif(word[1] in entity_lists):
                    ent = etree.SubElement(sent, "entity")
                    ent.set('class', word[1])
                    ent.set('index', 'T'+str(i))
                    i+=1
                    ent.set('negation', 'N')
                    ent.set('relation', word[2])
                    ent.set('start', str(text.find(word[0])))
                    ent.text = word[0]
        textsent.text = t.replace(' . ', '.')

        tree = etree.ElementTree(root)
        tree.write(xml_output, pretty_print=True, xml_declaration=True, encoding="utf-8")
        
def split_criteria(trial_text):
    in_crit, ex_crit = trial_text.split('\n')
    in_crit = in_crit.rstrip('\r')
    ex_crit = ex_crit.rstrip('\r')
    
    return in_crit, ex_crit

def find_trial(ID):
    page = requests.get('https://ensaiosclinicos.gov.br/rg/'+ID).text
    soup = BeautifulSoup(page, "lxml")
    lis = soup.find_all("li")
    
    for li in lis:
        ps = li.find_all("span", class_="label")
        if(ps):
            for p in ps:
                if(p.text == 'Inclusion criteria:'):
                    inclusion = li
                elif(p.text == 'Exclusion criteria:'):
                    exclusion = li
    
    for div in inclusion.find_all('div'):
        if(div.find("h2").text == 'pt-br'):
            incl_crit = [p.text for p in div.find_all("p")]
            #print("Inclusion Criteria: ", incl_crit[0], "\n\n")
    
    for div in exclusion.find_all('div'):
        if(div.find("h2").text == 'pt-br'):
            excl_crit = [p.text for p in div.find_all("p")]
            #print("Exclusion Criteria: ", excl_crit[0])
     
    return incl_crit[0], excl_crit[0]

def merge_XML(out_folder, name):
    xml_files = glob.glob(out_folder+"/*NER.xml") 
    xml_data = None
    for filename in xml_files:
        data = ET.parse(filename).getroot()
        if xml_data is None:
            xml_data = data
        else:
            xml_data.extend(data)
    if xml_data is not None:
        with open(out_folder+'/'+name+'_result.xml', 'w') as file:
            file.write(ET.tostring(xml_data).decode('utf-8'))
            
    return out_folder+'/'+name+'_result.xml'

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

def isTimeRelated(sent):
    time_trigs = ['anos', 'ano', 'mês', 'mes', 'meses', 'dia', 'dias', 'ms', 's', 'min', 'h']
    tsent = sent.lower()
    for t in time_trigs:
        match = re.search(t, tsent)
        if match:
            return True
    return False
    
def add_relation(xml_dir):
    tree = ET.ElementTree(file=xml_dir)
    root = tree.getroot()
    for crit in root:
        for sent in crit.findall("sent"):
            for ent in sent.findall("entity"):
                rel = ent.attrib["relation"]
                if rel == "":
                    ent.attrib["relation"] = 'None'
                    continue
                else:
                    for at in sent.findall("attribute"):
                        if rel[:2] == at.attrib["temp"]:
                            ent.attrib["relation"] =  re.sub(rel[:2], at.attrib["index"], rel)
                            
            for at in sent.findall("attribute"):
                at.attrib.pop("temp", None)
            
    for crit in root:
        for sent in crit.findall("sent"):
            previous = None
            for child in sent:
                if child.tag == 'text':
                    continue
                if child.tag == 'attribute':
                    if child.attrib['pos_rel'] == 'before' and previous != None:
                        if child.attrib['class']=='Anatomic_Location':
                            rel = 'located_in' 
                        elif isTimeRelated(child.text):
                            rel = 'has_tempMea'
                        else:
                            rel = 'has_value'
                        if previous.attrib['relation'] == 'None':
                            previous.attrib['relation'] = child.attrib['index']+':'+rel
                        else:
                            previous.attrib['relation']+= '|'+child.attrib['index']+':'+rel  
                if child.tag == 'entity' and child.attrib['relation'][3:]!='is_mea':
                    previous = child
    
    #child.attrib.pop('pos_rel', None)
    
    with open(xml_dir, 'wb') as file:
        tree.write(file)
    
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

def lookForSTR(word, mrconso):
    word = word.lower()
    mrconso.select((mrconso['14'] == word))
    query = mrconso.evaluate(mrconso['0'], selection=True)
    if query:
        cui = str(query[0])
        #print(f'Achei a CUI = {cui} para {word}!')
        return cui
    else:
        #print(f'Nao achei nenhuma CUI para {word}!')
        return None    
    
def lookForCUI(cui, mrsty):
    mrsty.select((mrsty['0'] == cui))
    query = mrsty.evaluate(mrsty['1'], selection=True)
    if query:
        tag = str(query[0])
        #print(f'Achei a tag "{tag}" para a CUI {cui}!')
        return sty2ellie[tag]
    else:
        #print(f'Nao achei nenhuma tag para a CUI {cui}!')
        return None
    
def make_ngrams(s, n):
    n = len(s) if len(s) < n else n
    ngrams = []
    for x in range(1, n+1):
        group = []
        for i in range(len(s) - x + 1):
            temp = ''
            for w in s[i:i + x]:
                temp+= w + ' '
            group.append(temp[:-1])
        ngrams.append(group)
    return ngrams

def findMeasuresAndConcepts(text, trigs, ops):
    mea = []
    ind = 0
    for op in ops:
        pattern = f'\s({op})\s(\d+|\d+\,\d+|\d+\.\d+)\s(\w+)\sde\s(\w+)\s'                      #op X t de Z
        match = re.findall(pattern, text)
        if match:
            for m in match:
                test = m[0].split()
                if len(test) > 1:
                    mea.append((test[0], 'B-Measurement', f'T{ind}', 'has'))
                    for t in test[1:]:
                        mea.append((t, 'I-Measurement', f'T{ind}', 'has'))
                else:
                    mea.append((m[0], 'B-Measurement', f'T{ind}', 'has'))
                mea.append((m[1], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[2], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[3], 'B-Concept', f'T{ind}:has_value'), 'has')
                ind+=1

        pattern = f'\s({op})\s(\d+|\d+\,\d+|\d+\.\d+)\s(\w+)\s(?!de\s)'                          #op X t
        match = re.findall(pattern, text)
        if match:
            for m in match:
                test = m[0].split()
                if len(test) > 1:
                    mea.append((test[0], 'B-Measurement', f'T{ind}', 'before'))
                    for t in test[1:]:
                        mea.append((t, 'I-Measurement', f'T{ind}', 'before'))
                else:
                    mea.append((m[0], 'B-Measurement', f'T{ind}', 'before'))
                mea.append((m[1], 'I-Measurement', f'T{ind}', 'before'))
                mea.append((m[2], 'I-Measurement', f'T{ind}', 'before'))
                ind+=1
    
    for t in trigs:
        auxMea = []
        for op in ops:
            pattern = f'(?<!{op})\s(((\d+|\d+\,\d+|\d+\.\d+)\s?({t}))\sde\s(\w+)?)\s'   #!op X t de Z
            match = re.finditer(pattern, text)
            if match:
                for m in match:
                    span = m.span()
                    temp = text[span[0]-15:span[1]]
                    out = False
                    for o in ops:
                        if re.search(f'{o}', temp):
                            out = True
                    if out: continue
                    pattern = f'(?<!\d\s.)\s(((\d+|\d+\,\d+|\d+\.\d+)\s?({t}))\sde\s(\w+)?)\s'   #!(Y (e|a)) X t de Z
                    match = re.findall(pattern, temp)
                    if match:
                        for m in match:
                            tempMea = []
                            tempMea.append((m[2], 'B-Measurement', f'T{ind}', 'has'))
                            tempMea.append((m[3], 'I-Measurement', f'T{ind}', 'has'))
                            tempMea.append((m[4], 'B-Concept', f'T{ind}:has_value', 'has'))
                            if tempMea not in auxMea:
                                auxMea.append(tempMea)
                                ind+=1
            
            pattern = f'(?<!{op})\s((\d+|\d+\,\d+|\d+\.\d+)\s?({t}))\s(?!de\s)'   #!op X t
            match = re.finditer(pattern, text)
            if match:
                for m in match:
                    span = m.span()
                    temp = text[span[0]-15:span[1]]
                    out = False
                    for o in ops:
                        if re.search(f'{o}', temp):
                            out = True
                    if out: continue
                    pattern = f'(?<!\d\s.)\s((\d+|\d+\,\d+|\d+\.\d+)\s?({t}))\s(?!de\s)'   #!(Y (e|a)) X t
                    match = re.findall(pattern, temp)
                    if match:
                        for m in match:
                            tempMea = []
                            tempMea.append((m[1], 'B-Measurement', f'T{ind}', 'before'))
                            tempMea.append((m[2], 'I-Measurement', f'T{ind}', 'before'))
                            if tempMea not in auxMea:
                                auxMea.append(tempMea)
                                ind+=1
        
        for match in auxMea:
            for m in match:
                mea.append(m)
        
        pattern = f'\s(entre)\s(\d+|\d+\,\d+|\d+\.\d+)\s(e)\s(\d+|\d+\,\d+|\d+\.\d+)\s?({t})\sde\s(\w+)\s'  #entre X e Y t de Z
        match = re.findall(pattern, text)
        if match:
            for m in match:
                mea.append((m[0], 'B-Measurement', f'T{ind}', 'has'))
                mea.append((m[1], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[2], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[3], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[4], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[5], 'B-Concept', f'T{ind}:has_value', 'has'))
                ind+=1
                
        pattern = f'\s(entre)\s(\d+|\d+\,\d+|\d+\.\d+)\s(e)\s(\d+|\d+\,\d+|\d+\.\d+)\s?({t})\s(?!de\s)'       #entre X e Y t
        match = re.findall(pattern, text)
        if match:
            for m in match:
                mea.append((m[0], 'B-Measurement', f'T{ind}', 'before'))
                mea.append((m[1], 'I-Measurement', f'T{ind}', 'before'))
                mea.append((m[2], 'I-Measurement', f'T{ind}', 'before'))
                mea.append((m[3], 'I-Measurement', f'T{ind}', 'before'))
                mea.append((m[4], 'I-Measurement', f'T{ind}', 'before'))
                ind+=1
        
        pattern = f'\s(de)\s(\d+|\d+\,\d+|\d+\.\d+)\s(a)\s(\d+|\d+\,\d+|\d+\.\d+)\s?({t})\sde\s(\w+)\s'      #de X a Y t de Z
        match = re.findall(pattern, text)
        if match:
            for m in match:
                mea.append((m[1], 'B-Measurement', f'T{ind}', 'has'))
                mea.append((m[2], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[3], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[4], 'I-Measurement', f'T{ind}', 'has'))
                mea.append((m[5], 'B-Concept', f'T{ind}:has_value', 'has'))
                ind+=1
                
        pattern = f'\s(de)\s(\d+|\d+\,\d+|\d+\.\d+)\s(a)\s(\d+|\d+\,\d+|\d+\.\d+)\s?({t})\s(?!de\s)'          #de X a Y t
        match = re.findall(pattern, text)
        if match:
            for m in match:
                mea.append((m[1], 'B-Measurement', f'T{ind}', 'before'))
                mea.append((m[2], 'I-Measurement', f'T{ind}', 'before'))
                mea.append((m[3], 'I-Measurement', f'T{ind}', 'before'))
                mea.append((m[4], 'I-Measurement', f'T{ind}', 'before'))
                ind+=1
        
    return mea

def findUMLS(crit, n):
    #Open the UMLs tables
    mrconso = vaex.open("models/mrconso(POR).hdf5")
    mrsty = vaex.open("models/mrsty.hdf5")  
    
    #SET UP THE STOPWORDS
    stopwords = SW.words('portuguese')
    stopwords.remove('não')
    stopwords = stopwords + ['ser', 'ter', 'têm', 'havia', '.']
    
    #SET UP THE NEGATION LIST
    with open('models/negationTerms.txt', encoding='utf8') as f:
        negList = f.read().splitlines()
    
    umls = []
    for sentences in crit:
        tags = []
        mea = []
        for sent in sentences:
            #MEASUREMENT AND CONCEPTS
            mea.append(findMeasuresAndConcepts(sent, triggers, operators))
            #TOKENIZE
            words = word_tokenize(sent, language='portuguese')

            #CLEAN
            clean_words = []
            for word in words:
                if word not in stopwords:
                    clean_words.append(word)

            #SPLIT BY COMMAS
            trig = True
            split_clean_words = []
            while(trig):
                try:
                    index = clean_words.index(',')
                    split_clean_words.append(clean_words[:(index)])
                    clean_words = clean_words[index+1:]
                except:
                    trig = False
            split_clean_words.append(clean_words)

            #SET UP THE CANDIDATES
            candidates = []
            for clean_words in split_clean_words:
                ngrams = make_ngrams(clean_words, n)
                candidates.append(ngrams)

            #SEARCH IN THE DATABASE
            results = []
            for group in candidates:
                found = []
                for span in reversed(group):
                    for cand in span:
                        match = False
                        for s in found:
                            if cand in s: match = True
                        if match:
                            continue
                        cui = lookForSTR(cand, mrconso)
                        if cui != None:
                            tag = lookForCUI(cui, mrsty)
                            #print((cui, cand, tag))
                            #print(cand)
                            results.append((cui, cand, tag))
                            found.append(cand)
                        elif cand in negList:
                            results.append(('', cand, 'Negation'))
            tags.append([tag for tag in results])

        tags2 = []
        for tagset in tags:
            temp = []
            for tag in tagset:
                test = tag[1].split()
                if len(test) > 1:
                    temp.append((tag[0], test[0], 'B-'+tag[2]))
                    for t in test[1:]:
                        temp.append((tag[0], t, 'I-'+tag[2]))
                else:
                    temp.append((tag[0], tag[1], 'B-'+tag[2]))
            tags2.append(temp)

        result = []
        for tagset, mset, sent in zip(tags2, mea, sentences):
            temp = []
            marked = []
            words = word_tokenize(sent, language='portuguese')
            flag = 0  #flag pra impedir que termos sejam marcados randomicamente na frase
            for word in words:
                t = 'O'
                r = ''
                aux = ''
                w = word.lower()
                for mtag in mset: #Measurement 
                    if w==mtag[0].lower() and mtag not in marked:
                        iob = mtag[1][0]
                        if (iob=='I' and flag==1) or iob=='B':
                            t = mtag[1]
                            r = mtag[2]
                            aux = mtag[3]
                            flag = 1
                            marked.append(mtag)
                            break
                if r=='': flag = 0
                for tag in tagset: #UMLs and Negation
                    if w==tag[1].lower():
                        t = tag[2]
                        if r!='':
                            r = r + ':is_mea'
                        if t[2:] == 'Anatomic_Location':
                            aux = 'before'
                temp.append((word, t, r, aux))
            result.append(temp)
                
        umls.append(result)
        
    return umls 

def main(file_name, inp, out, ec_id):    
    input_dir = inp
    text_file = file_name
    crit_id = ec_id
    output_dir = out
    
    if(text_file != '' and crit_id == ''):
        try:
            print("Reading text file from ", input_dir+'/'+text_file)
            with open(input_dir+'/'+text_file, 'r', encoding='UTF-8') as f:
                trial = f.read()
            in_crit, ex_crit = split_criteria(trial) #separate inclusion and exclusion criteria
        except:
            print("Error 02!")
            sys.exit(1)
        else:
            print("File successfully opened.\n")
        
    elif(text_file == '' and crit_id != ''):
        try:
            print("Looking for trial with ID = ", crit_id)
            in_crit, ex_crit = find_trial(crit_id)
        except:
            print("Error 03!")
            sys.exit(1)
        else:
            print("Trial ", crit_id, " successfully found.\n")
        
    else:
        print("Error 01!")
        sys.exit(1)
    
    #create a list out of inclusion and exclusion criteria
    criteria = [in_crit, ex_crit]
    
    #Progression bar
    bar = IncrementalBar('Extracting Eligibility Criteria', max = 10, suffix='%(percent)d%%')
    bar.next()
    
    #create NER xml file name
    if(text_file != ''):
        name = re.search('^(.*)\.txt',text_file)
        if name:
            filename = name.group(1)
    else:
        filename = crit_id 
    output_ner_in = output_dir+'/'+filename+'_Inclusion_NER.xml'
    output_ner_ex = output_dir+'/'+filename+'_Exclusion_NER.xml'

    bar.next()

    #split the sentences
    sents_criteria = []
    for crit in criteria:
        text = crit.replace(';', '.')
        temp_sents = text.split("\n")
        sents = []
        for sent in temp_sents:
            s = sent_tokenize(sent, language='portuguese')
            sents.extend(s)
        sents_criteria.append(sents)
      
    bar.next()  
      
    #clean and filter EC
    clean_criteria = []
    for sents in sents_criteria: 
        clean_sents = []
        for sent in sents:
            clean_sent = normalize(sent)
            filtered_sent = ec_filter(clean_sent)
            if filtered_sent:
                clean_sents.append(filtered_sent)
        clean_criteria.append(clean_sents)  
    
    bar.next()
    
    #run umls
    umls = findUMLS(clean_criteria, 4)
    
    bar.next()
    
    #generate xml file
    generate_XML(in_crit, umls[0], output_ner_in, 0)
    generate_XML(ex_crit, umls[1], output_ner_ex, 1)
    
    bar.next()
    
    #predict negation for entities
    add_negation(output_ner_in)
    add_negation(output_ner_ex)
    
    bar.next()
    
    #extract relations
    add_relation(output_ner_in)
    add_relation(output_ner_ex)
    
    bar.next()
    
    #merge XMLS
    
    result_dir = merge_XML(output_dir, filename)
    
    bar.next()
    
    #Delete temporary files
    os.remove(output_ner_in)
    os.remove(output_ner_ex)
    
    bar.next()
    
    #Done
    bar.finish()
    print(f'\nSaving file to {result_dir}')
    return result_dir