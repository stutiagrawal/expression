import pipelineUtil
import os
import xml.etree.ElementTree as ET
import argparse

def get_xml(dirname, analysis_id, logger):

    print "Downloading XML"
    print "Analysis ID = %s" % analysis_id
    xml_file = "%s.xml" %os.path.join(dirname, analysis_id)
    cmd = ['cgquery', '-o' , xml_file, 'analysis_id=%s' %analysis_id]
    pipelineUtil.log_function_time('cgquery', analysis_id, cmd, logger)

    return xml_file

def get_value_from_tree(result, field):
    if not (result == None):
        if not (result.find(str(field)) == None):
            field_value = result.find(str(field)).text
            if field_value == None:
                return ""
            else:
                return field_value
    else:
        raise Exception("Empty result from XML")

def extract_metadata(dirname, analysis_id, logger):

    #Download the xml file
    xml_file = get_xml(dirname, analysis_id, logger)

    #Parse XML to get required fields
    tree = ET.parse(xml_file)
    root = tree.getroot()
    metadata = dict()
    for result in root.iter("Result"):
        metadata["participant_id"] = get_value_from_tree(result, "participant_id")
        metadata["sample_id"] = get_value_from_tree(result, "sample_id")
        metadata["disease"] = get_value_from_tree(result, "disease_abbr")
        metadata["tss_id"] = get_value_from_tree(result, "tss_id")
        metadata["library_strategy"] = get_value_from_tree(result, "library_strategy")
        metadata["analyte_code"] = get_value_from_tree(result, "analyte_code")
        metadata["sample_type"] = get_value_from_tree(result, "sample_type")
        metadata["platform"] = get_value_from_tree(result, "platform")
        metadata["aliquot_id"] = get_value_from_tree(result, "aliquot_id")

    for result in root.iter("ResultSummary"):
        metadata["downloadable_file_size"] = get_value_from_tree(result, "downloadable_file_size")
    os.remove(xml_file)
    return metadata


def collect_metrics(sub_dir):
    f = open("metrics_cuff.txt", "w")
    for log_file in os.listdir(sub_dir):
        if log_file.endswith(".log"):
            analysis_id = log_file.split(".")[0]
            metadata = extract_metadata(sub_dir, analysis_id, None)
            log_file = os.path.join(sub_dir, log_file)
            logp = open(log_file, "r")
            for line in logp:
                if "CUFFLINKS_TIME" in line:
                    line = line.split()
                    f.write("%s\t%s\t%s\n" %(line[4], line[5], metadata["downloadable_file_size"]))
    f.close()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='label_dataset.py')
    parser.add_argument('--dirname', default='/home/ubuntu/SCRATCH/lung_results')
    args = parser.parse_args()
    collect_metrics(args.dirname)

"""
    for filename in os.listdir(args.dirname):
        if filename.endswith('fpkm_tracking'):
            analysis_id = filename.split(".")[0]
            metadata = extract_metadata(args.dirname, analysis_id, None)
            print 'disease= %s' %metadata['disease']
            print metadata
            if metadata['disease'] != "":
                if not os.path.isdir(os.path.join(args.dirname, metadata['disease'])):
                    os.mkdir(os.path.join(args.dirname, metadata['disease']))
            cmd = ['mv', '%s' % os.path.join(args.dirname, filename), '%s' %os.path.join(args.dirname, metadata["disease"], '%s_%s' %(metadata['disease'], analysis_id))]
            pipelineUtil.log_function_time('mv', analysis_id, cmd, None)
"""
