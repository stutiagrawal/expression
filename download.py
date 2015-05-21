import pipelineUtil
import os
import argparse

def download(analysis_id, cghub_key, output_dir, bucket):

    pipelineUtil.retrieve_data(analysis_id, cghub_key, output_dir)

    local_input = os.path.join(output_dir, analysis_id)
    pipelineUtil.upload_to_cleversafe(None, bucket, local_input)

    pipelineUtil.remove_dir(local_input)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='download.py')
    parser.add_argument('analysis_id', help='analysis id')

    args = parser.parse_args()

    output_dir = '/home/ubuntu/SCRATCH/lung'
    cghub_key = '/home/ubuntu/cghub.key'
    bucket = 's3://bioinformatics_scratch'

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    f = open(args.analysis_id, "r")
    for line in f:
        analysis_id = line.strip()
        download(analysis_id, cghub_key, output_dir, bucket)
    f.close()
