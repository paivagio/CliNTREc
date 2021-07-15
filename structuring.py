# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 18:15:16 2021

@author: paiva
"""
import os
import re

from xml.etree import ElementTree as ET
from lxml import etree

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def pacientStructuring(inPath, outPath):
    tags = ['Condition','Observation','Procedure_Device','Drug_Substance', 'Concept']
    
    tree=ET.ElementTree(file=inPath)
    filename = re.sub('.xml', '_structured.xml', inPath.split('/')[-1])
    outFile = os.path.join(outPath, filename)            
    
    
    root = tree.getroot()            #source XML
    newroot = etree.Element("root")  #structured XML
    
    sub = etree.SubElement(newroot, "ID")
    sub.text = root.find('ID').text
    sub = etree.SubElement(newroot, "AGE")
    sub.text = root.find('AGE').text
    sub = etree.SubElement(newroot, "GENDER")
    sub.text = root.find('GENDER').text
    sub = etree.SubElement(newroot, "BIRTH")
    sub.text = root.find('BIRTH').text
    sub = etree.SubElement(newroot, "CID")
    sub.text = root.find('CID').text
    
    #Append the sentences text to the top of the section
    for n, sent in enumerate(root.findall('sent')):
        t = etree.SubElement(newroot, 'text')
        t.set('id', str(n))
        t.text = sent.find('text').text
    
    #Group up the entities with the same tag and append to the section
    cond = etree.SubElement(newroot, 'CONDITIONS')
    obs = etree.SubElement(newroot, 'OBSERVATIONS') 
    proc = etree.SubElement(newroot, 'PROCEDURES_DEVICES')
    drug = etree.SubElement(newroot, 'DRUGS_SUBSTANCES')
    conc = etree.SubElement(newroot, 'CONCEPTS')
    instances = [cond, obs, proc, drug, conc]
    
    for obj, tag in zip(instances, tags):
        for n, sent in enumerate(root.findall('sent')):
            for ent in sent.findall('entity'):
                if ent.attrib['class'] != tag:
                    continue
                new_ent = etree.SubElement(obj, tag)
                new_ent.set('text_id', str(n))
                new_ent.set('negated', ent.attrib['negation'])
                new_ent.text = ent.text
                
                rel = ent.attrib['relation']
                if rel != '' and rel[3:] != 'is_mea':
                    relations = rel.split('|')
                    value = ''
                    time = ''
                    place = ''
                    for r in relations:
                        index = r[:2]
                        r_tag = r[3:]
                        for at in sent.findall('attribute'):
                            if at.attrib['index'] == index:
                                if r_tag == 'has_value':
                                    value+= ', '+at.text
                                if r_tag == 'has_tempMea':
                                    time+= ', '+at.text
                                if r_tag == 'located_in':
                                    place+= ', '+at.text
                    new_ent.set('value', value[2:]) 
                    new_ent.set('time', time[2:])
                    new_ent.set('place', place[2:])
                else:
                    new_ent.set('value', '')
                    new_ent.set('time', '')
                    new_ent.set('place', '')
                    
    print(f'Saving restructured file to {outFile}\n')
    tree = etree.ElementTree(newroot)
    tree.write(outFile, pretty_print=True, xml_declaration=True, encoding="utf-8")
        
def ecStructuring(inPath, outPath):
    tags = ['Condition','Observation','Procedure_Device','Drug_Substance', 'Concept']
        
    tree=ET.ElementTree(file=inPath)
    filename = re.sub('.xml', '_structured.xml', inPath.split('/')[-1])
    outFile = os.path.join(outPath, filename)               
    
    root = tree.getroot()            #source XML
    newroot = etree.Element("root")  #structured XML
    
    name = etree.SubElement(newroot, "ID")
    name.text = re.sub('_result.xml', '', filename)
    age = etree.SubElement(newroot, "AGE")
    age.text = 'any'
    sex = etree.SubElement(newroot, "GENDER")
    sex.text = 'any'
    
    for sent in root.find('Inclusion').findall('sent'):
        for at in sent.findall('attribute'):
            if at.attrib['class'] != 'Measurement':
                continue
            text = at.text
            match = re.search(' anos', text)
            if not match:
                continue
            age.text = text
            
    for sent in root.find('Inclusion').findall('sent'):
        for t in sent.findall('text'):
            text = t.text.lower()
            match = re.search('mulher|feminino|mama|vagina', text)
            if match:
                sex.text = 'F'
            match = re.search('homem|homens|masculino|testiculo|penis', text)
            if match:
                if sex.text == 'F':
                    sex.text = 'any'
                else:
                    sex.text = 'M'
    
    inc = etree.SubElement(newroot, "INCLUSION")
    exc = etree.SubElement(newroot, "EXCLUSION")
    
    #Append the sentences text to the top of the section
    for n, sent in enumerate(root.find('Inclusion').findall('sent')):
        t = etree.SubElement(inc, 'text')
        t.set('id', str(n))
        t.text = sent.find('text').text
    
    for n, sent in enumerate(root.find('Exclusion').findall('sent')):
        t = etree.SubElement(exc, 'text')
        t.set('id', str(n))
        t.text = sent.find('text').text
    
    #Group up the entities with the same tag and append to the section
    cond = etree.SubElement(inc, 'CONDITIONS')
    obs = etree.SubElement(inc, 'OBSERVATIONS') 
    proc = etree.SubElement(inc, 'PROCEDURES_DEVICES')
    drug = etree.SubElement(inc, 'DRUGS_SUBSTANCES')
    conc = etree.SubElement(inc, 'CONCEPTS')
    instances = [cond, obs, proc, drug, conc]
    
    for obj, tag in zip(instances, tags):
        for n, sent in enumerate(root.find('Inclusion').findall('sent')):
            for ent in sent.findall('entity'):
                if ent.attrib['class'] != tag:
                    continue
                new_ent = etree.SubElement(obj, tag)
                new_ent.set('text_id', str(n))
                new_ent.set('negated', ent.attrib['negation'])
                new_ent.text = ent.text
                
                rel = ent.attrib['relation']
                if rel != '' and rel[3:] != 'is_mea':
                    relations = rel.split('|')
                    value = ''
                    time = ''
                    place = ''
                    for r in relations:
                        index = r[:2]
                        r_tag = r[3:]
                        for at in sent.findall('attribute'):
                            if at.attrib['index'] == index:
                                if r_tag == 'has_value':
                                    value+= ', '+at.text
                                if r_tag == 'has_tempMea':
                                    time+= ', '+at.text
                                if r_tag == 'located_in':
                                    place+= ', '+at.text
                    new_ent.set('value', value[2:]) 
                    new_ent.set('time', time[2:])
                    new_ent.set('place', place[2:])
                else:
                    new_ent.set('value', '')
                    new_ent.set('time', '')
                    new_ent.set('place', '')
    
    cond = etree.SubElement(exc, 'CONDITIONS')
    obs = etree.SubElement(exc, 'OBSERVATIONS') 
    proc = etree.SubElement(exc, 'PROCEDURES_DEVICES')
    drug = etree.SubElement(exc, 'DRUGS_SUBSTANCES')
    conc = etree.SubElement(exc, 'CONCEPTS')
    instances = [cond, obs, proc, drug, conc]
    
    for obj, tag in zip(instances, tags):
        for n, sent in enumerate(root.find('Exclusion').findall('sent')):
            for ent in sent.findall('entity'):
                if ent.attrib['class'] != tag:
                    continue
                new_ent = etree.SubElement(obj, tag)
                new_ent.set('text_id', str(n))
                new_ent.set('negated', ent.attrib['negation'])
                new_ent.text = ent.text
                
                rel = ent.attrib['relation']
                if rel != '' and rel[3:] != 'is_mea':
                    relations = rel.split('|')
                    value = ''
                    time = ''
                    place = ''
                    for r in relations:
                        index = r[:2]
                        r_tag = r[3:]
                        for at in sent.findall('attribute'):
                            if at.attrib['index'] == index:
                                if r_tag == 'has_value':
                                    value+= ', '+at.text
                                if r_tag == 'has_tempMea':
                                    time+= ', '+at.text
                                if r_tag == 'located_in':
                                    place+= ', '+at.text
                    new_ent.set('value', value[2:]) 
                    new_ent.set('time', time[2:])
                    new_ent.set('place', place[2:])
                else:
                    new_ent.set('value', '')
                    new_ent.set('time', '')
                    new_ent.set('place', '')
    
    print(f'Saving restructured file to {outFile}\n')
    tree = etree.ElementTree(newroot)
    tree.write(outFile, pretty_print=True, xml_declaration=True, encoding="utf-8")
    return outFile      