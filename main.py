# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 16:09:50 2021

@author: paiva
"""

import os
import argparse, sys, logging
import umls as UMLS
import ner as NER
import structuring as structure
import cohort_selection as CS

# define the script global logger
def strd_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.ERROR)
    logging.disable(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', "%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

# processing the command line options
def _process_args():
    parser = argparse.ArgumentParser(description='CliNTRec - HAILab')

    # path to input Folder
    parser.add_argument('-i', default='temp', type = str,  help='Input Folder (default: temp)')
    
    # text file name with eligibility criteria
    parser.add_argument('-t', default= 'ec.txt', type = str, help='Eligibility criteria filename (default: ec.txt)')
    
    # text file name with pacients EHR
    parser.add_argument('-e', type = str, help = 'Pacients EHR filename (default: None)')
    
    # id from clinical trial from ensaiosclinicos.gov 
    parser.add_argument('-id', type = str, help='ID from clinical trial (default: None)')
    
    # Select cohort
    parser.add_argument('-s', default= False, type = bool, help = 'Run cohort selection system (default: False)')
    
    # output folder
    parser.add_argument('-o', default='temp', type=str, help='Output Folder (default: temp)')
    
    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    args = _process_args()
    log = strd_logger('clintrec-hailab')
    
    if not os.path.exists(args.o + '/ec'):
        os.makedirs(args.o + '/ec')
    if not os.path.exists(args.o + '/pacients'):
        os.makedirs(args.o + '/pacients')
    
    if not args.e:
        log.debug('Processing Clinical Trial! \n')
        
        #main(ec_filename, input_folder, out_folder, ec_id)
        if args.id:
            print('\n############ CLINICAL TRIAL ############\n')
            result_file = UMLS.main('', args.i, args.o, args.id)
            target_ec = structure.ecStructuring(result_file, args.o + '/ec')
            if args.s:
                CS.findMyPacients(target_ec, args.o + '/pacients/')
        else:
            file_type = args.t[(len(args.t)-3):]

            if file_type == 'xml' and args.s:
                print('\n############ COHORT SELECTION ############\n')
                CS.findMyPacients(args.i + '/ec/' + args.t, args.i + '/pacients/')
            else:
                print('\n############ CLINICAL TRIAL ############\n')
                result_file = UMLS.main(args.t, args.i, args.o, '')
                target_ec = structure.ecStructuring(result_file, args.o + '/ec')
                if args.s:
                    CS.findMyPacients(target_ec, args.o + '/pacients/')
    else:
        log.debug('Processing Pacients EHR! \n')
        print('\n############ PACIENT EHR ############\n')
        
        #main(ehr_filename, input_folder, output_folder)
        result_file = NER.main(args.e, args.i, args.o)
        structure.pacientStructuring(result_file, args.o+'/pacients')
    
    log.debug('Finished! \n')
    

