import argparse
import os
import pipelineUtil

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='fix_korean_data.py')
    parser.add_argument('--dirname', default='/home/ubuntu/SCRATCH/korea')
    args = parser.parse_args()


    for dirname in os.listdir(args.dirname):
        dirname = os.path.join(args.dirname, dirname)
        os.chdir(dirname)
        analysis_id = os.path.basename(dirname)
        s = list()
        if os.path.isfile("%s.tar" %(os.path.join(dirname,analysis_id))):
            print "%s.tar exists" %(os.path.join(dirname,analysis_id))
            continue
        for filename in os.listdir(dirname):
            #org_file = os.path.join(dirname, filename)
            if filename.endswith("txt.gz"):
                new_filename = filename.replace("txt", "fastq")
                #new_file = os.path.join(dirname, new_filename)
                cmd = ['mv', filename, new_filename]
                pipelineUtil.log_function_time('mv',analysis_id, cmd, None)
                s.append(new_filename)
            else:
                s.append(filename)
        tarfile = "%s.tar" % analysis_id
        cmd = ['tar', '-cf', tarfile]
        cmd = cmd + s
        pipelineUtil.log_function_time('tar',analysis_id, cmd, None)
        #cmd = ['mv', tarfile, dirname]
        #pipelineUtil.log_function_time('mv', analysis_id, cmd, None)
        print 'completed %s' %dirname
        remote_output = "%s/" %os.path.join('s3://bioinformatics_scratch', analysis_id)
        pipelineUtil.upload_to_cleversafe(None, remote_output, tarfile)
