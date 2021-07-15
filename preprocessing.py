# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 16:45:12 2021

@author: paiva
"""
import re, unicodedata

word2trig =    {'milimetros':'mm',
                'milímetros':'mm',
                'milímetro':'mm',
                'milimetro':'mm',
                'centimetros':'cm',
                'centímetros':'cm',
                'centímetro':'cm',
                'centimetro':'cm',
                'decimetros':'dc',
                'decímetros':'dc',
                'decímetro':'dc',
                'decimetro':'dc',
                'metros':'m',
                'metro':'m',
                'decametros':'dam',
                'decâmetros':'dam',
                'decametro':'dam',
                'decâmetro':'dam',
                'quilometros':'km',
                'quilômetros':'km',
                'quilômetro':'km',
                'quilometro':'km',
                'milisegundos':'ms',
                'milisegundo':'ms',
                'segundos':'s',
                'segundo':'s',
                'minutos':'min',
                'minuto':'min',
                'horas':'h',
                'hora':'h',
                'miligramas':'mg',
                'miligrama':'mg',
                'gramas':'g',
                'grama':'g',
                'quilogramas':'kg',
                'quilos':'kg',
                'quilo':'kg',
                'quilograma':'kg',
                'mililitros':'ml',
                'mililitro':'ml',
                'litros':'l',
                'litro':'l'}

word2number =  {'um':'1',
                'dois':'2',
                'duas':'2',
                'três':'3',
                'quatro':'4',
                'cinco':'5',
                'seis':'6',
                'sete':'7',
                'oito':'8',
                'nove':'9',
                'dez':'10',
                'onze':'11',
                'doze':'12',
                'treze':'13',
                'quatorze':'14',
                'quinze':'15',
                'dezesseis':'16',
                'dezessete':'17',
                'dezoito':'18',
                'dezenove':'19',
                'vinte':'20',
                'trinta':'30',
                'quarenta':'40',
                'cinquenta':'50',
                'sessenta':'60',
                'setenta':'70',
                'oitenta':'80',
                'noventa':'90',
                'cem':'100',
                'cento':'100',
                'duzentos':'200',
                'trezentos':'300',
                'quatrocentos':'400',
                'quinhentos':'500',
                'seiscentos':'600',
                'setecentos':'700',
                'oitocentos':'800',
                'novecentos':'900',
                'mil':'1000',
                'milhão':'1000000'}

triggers = ['mm', 'cm', 'dm', 'm', 'dam', 'hm', 'km', 'ms', 's',
            'min', 'h', 'hs', 'mg', 'ng', 'g', 'kg', 'ml', 'l',
            'anos', 'ano', 'mês', 'mes', 'meses', 'dia', 'dias',
            'mol', 'nmol', 'mmol', 'umol']

def cleanUnits(string, dic):
    for word in dic:
        change = dic[word]
        pattern = f'(\s{word}\s)'
        string = re.sub(pattern, ' '+change+' ', string)
    return string

def cleanNumbers(string, dic):
    for word in dic:
        change = dic[word]
        if word != 'um':
            pattern = f'(\s{word}\s)'
            string = re.sub(pattern, ' '+change+' ', string)
        else:
            for t in triggers:
                pattern = f'(\s{word}\s(?={t}\s))'
                string = re.sub(pattern, ' '+change+' ', string)
    return string

def normalize(rawtext):
    #normalize punctuation
    text=re.sub('>='," maior igual a ",rawtext)
    text=re.sub('<='," menor igual a ",text)
    text=re.sub(';',' ; ',text)
    text=re.sub('>>','~~~',text)
    text=re.sub('>',' maior que ',text)
    text=re.sub('<',' menor que ',text)
    text=re.sub('~~~','>>',text)
    text=re.sub('=', ' = ',text)
    text=re.sub('\:',' : ',text)
    text=re.sub('\[', ' [ ', text)
    text=re.sub('\]', ' ] ',text)
    text=re.sub('\(', ' ( ',text)
    text=re.sub('\)', ' ) ',text)
    
    #protect the decimal's '.' from the period normalization
    times = re.findall('\d+x\/\w+',text)
    for time in times:
        t = re.search('(\d+x)\/(\w+)', time)
        text = re.sub(t.group(1) + '\/' + t.group(2), t.group(1) + ' por ' + t.group(2), text)
        
    #protect the decimal's '.' from the period normalization
    decimals = re.findall('\d+\.\d+',text)
    for decimal in decimals:
        d = re.search('(\d+)\.(\d+)', decimal)
        text = re.sub(d.group(1) + '\.' + d.group(2), d.group(1) + 'SINALDECIMAL' + d.group(2), text)
    
    #protect the decimal's ',' from the comma normalization
    decimals = re.findall('\d+\,\d+',text)
    for decimal in decimals:
        d = re.search('(\d+)\,(\d+)', decimal)
        text = re.sub(d.group(1) + '\,' + d.group(2), d.group(1) + 'SINALVIRGULA' + d.group(2), text)
        
    #normalize gaps
    gaps=re.findall('\d-\d',text)
    for gap in gaps:
        g=re.search('(\d)-(\d)',gap)
        text=re.sub(g.group(1)+'-'+g.group(2),g.group(1)+' - '+g.group(2),text)
    
    #normalize periods
    periods = re.findall('\w\.\s?',text)
    for period in periods:
        p=re.search('(\w)\.\s?',period)
        text=re.sub(p.group(1)+'\.',p.group(1)+' . ',text)
        
    #normalize commas
    text=re.sub(',',' , ',text)
    
    #return the decimal's '.'
    text=re.sub('SINALDECIMAL','.',text)
    text=re.sub('SINALVIRGULA',',',text)
    
    text = cleanUnits(text, word2trig)
    text = cleanNumbers(text, word2number)
    
    return ' '+text+' '


keywords = ['consentir', 'estar de acordo', 'concordar', 'termos', 'parceiro', 'termo de consentimento', 'liberação',
            'motivos pessoais', 'tcle']

def ec_filter(sent):
    tsent = sent.lower()
    for keyword in keywords:
        match = re.search(keyword, tsent)
        if match:
            return None
    return sent
    

def clean2encode(text):
    text = text.lower()                                                                 #lowercase
    text = ''.join(c for c in unicodedata.normalize('NFD', text) 
                   if unicodedata.category(c) != 'Mn')                                  #retira acentos
    text = re.sub("[^A-Za-z']+", ' ', text)                                             #remove caractéres não alfa-numéricos
    return text