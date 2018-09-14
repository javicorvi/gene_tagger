import sys
import argparse
import ConfigParser
import re
import codecs
import os
from subprocess import call
import logging


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

parser=argparse.ArgumentParser()
parser.add_argument('-p', help='Path Parameters')
args=parser.parse_args()
parameters={}
if __name__ == '__main__':
    import gene_tagger
    parameters = gene_tagger.ReadParameters(args)     
    gene_tagger.Main(parameters)

def Main(parameters):
    inputDirectory=parameters['inputDirectory']
    outputDirectory= parameters['outputDirectory']
    index_id=int(parameters['index_id'])
    index_text_to_tag= int(parameters['index_text_to_tag'])
    tagging(inputDirectory, outputDirectory, index_id, index_text_to_tag)
    
    
    
def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['inputDirectory']=Config.get('MAIN', 'inputDirectory')
        parameters['outputDirectory']=Config.get('MAIN', 'outputDirectory')
        parameters['index_id']=Config.get('MAIN', 'index_id')
        parameters['index_text_to_tag']=Config.get('MAIN', 'index_text_to_tag')
    else:
        logging.error("Please send the correct parameters config.properties --help ")
        sys.exit(1)
    return parameters   

def tagging(input_dir, output_dir, index_id, index_text_to_tag):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_dir + "pubtator_format/"):
        os.makedirs(output_dir + "pubtator_format/")    
    ids_list=[]
    if(os.path.isfile(output_dir+"/list_files_processed.dat")):
        with open(output_dir+"/list_files_processed.dat",'r') as ids:
            for line in ids:
                ids_list.append(line.replace("\n",""))
    if os.path.exists(input_dir):
        onlyfiles_toprocess = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if (os.path.isfile(os.path.join(input_dir, f)) & f.endswith('.xml.txt') & (os.path.basename(f) not in ids_list))]
    #first standardization to all
    with open(output_dir+"/list_files_processed.dat",'a') as list_files:    
        for file in onlyfiles_toprocess:    
            process(file, output_dir, index_id, index_text_to_tag)
            list_files.write(os.path.basename(file)+"\n")
            list_files.flush()
    

def process(input_file, output_dir, index_id, index_text_to_tag):
    logging.info("Tagging intup file  : " + input_file + " ,  output directory : "  + output_dir)
    total_articles_errors = 0
    internal_folder = output_dir + "pubtator_format/" + os.path.basename(input_file)+"_"
    if not os.path.exists(internal_folder):
        os.makedirs(internal_folder)  
    pubtator_format_file_path = internal_folder + "/" + os.path.basename(input_file)
    output_file = output_dir +  os.path.basename(input_file)
    with codecs.open(input_file,'r',encoding='utf8') as file:
        with codecs.open(pubtator_format_file_path,'w',encoding='utf8') as new_file:
            for line in file:
                try:
                    data = re.split(r'\t+', line) 
                    if(len(data)==5):
                        id = data[index_id]
                        text_to_tag = data[index_text_to_tag]
                        new_file.write(id+"|t|"+text_to_tag)
                        new_file.write("\n")
                        new_file.flush()
                    else:
                        logging.error("The article with line:  " + line)
                        logging.error("Belongs to : " + input_file + " and does not have four columns")
                        total_articles_errors = total_articles_errors + 1
                except Exception as inst:
                    logging.error("The article with id : " + id + " could not be processed. Cause:  " +  str(inst))
                    logging.error("Belongs to : " + input_file )
                    logging.debug( "Full Line :  " + line)
                    logging.error("The cause probably: contained an invalid character ")
                    total_articles_errors = total_articles_errors + 1
    call_gene_tagger(internal_folder, output_dir)
    logging.info("Tagging  Finish For " + input_file + ".  output file : "  + output_file + ", articles with error : " + str(total_articles_errors))    
        


def call_gene_tagger(input_folder, output_file):
    gnormPlus_exe_path = "GNormPlus.jar"
    setup_path = "setup.txt" 
    resp = call(["java", "-Xmx10G", "-Xms10G", "-jar", gnormPlus_exe_path, input_folder, output_file , setup_path])
    if(resp==1):
        logging.error("GNormPlus error, Tagging input folder  : " + input_folder + ".  output file : "  + output_file)
    
