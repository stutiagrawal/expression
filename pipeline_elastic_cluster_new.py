import os
import pipelineUtil
import argparse
import setupLog
import logging

def run_pipeline(args, workdir, analysis_id, logger):
    """ align datasets using STAR and compute expression using cufflinks """

    for filename in os.listdir(workdir):
        if filename.endswith(".tar") or filename.endswith(".tar.gz"):
            tar_file_in = os.path.join(workdir, filename)
            break

    star_output_dir = os.path.join(workdir, 'star_2_pass')
    if os.path.isdir(star_output_dir):
        pipelineUtil.remove_dir(star_output_dir)
    os.mkdir(star_output_dir)
    bam = "%s_star.bam" %os.path.join(star_output_dir, analysis_id)

    if not os.path.isfile(bam):
        star_cmd = ['time', '/usr/bin/time', 'python', args.star_pipeline,
                    '--genomeDir', args.genome_dir,
                    '--runThreadN', args.p,
                    '--tarFileIn', tar_file_in,
                    '--workDir', workdir,
                    '--out', bam,
                    '--genomeFastaFile', args.genome_fasta_file,
                    '--sjdbGTFfile', args.gtf
                   ]
        if args.quantMode != "":
            star_cmd.append('--quantMode')
            star_cmd.append(args.quantMode)

    pipelineUtil.log_function_time("STAR", analysis_id, star_cmd, logger)

    cufflinks_cmd = ['time', '/usr/bin/time', 'python', args.cufflinks_pipeline,
                     '--bam', bam,
                     '--gtf', args.gtf,
                     '--analysis_id', analysis_id,
                     '--out', star_output_dir,
                     '--p', args.p,
                     '--multi_read_correct', 'True'
                    ]

    pipelineUtil.log_function_time("CUFFLINKS", analysis_id, cufflinks_cmd, logger)

    #pipelineUtil.remove_dir(star_output_dir)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='pipeline.py', description='STAR and cufflinks')
    parser.add_argument('--analysis_id', required=True, default=None, type=str, help='analysis ids')
    parser.add_argument('--gtf', required=True, type=str, help='genome annotation file')
    parser.add_argument('--p', type=str, default=1, help='number of threads')

    star = parser.add_argument_group("star pipeline")
    star.add_argument('--genome_dir', default='/home/ubuntu/SCRATCH/star_genome_d1_vd1_gtfv22/', required=True,
                     help='star index directory')
    star.add_argument('--star_pipeline', default='/home/ubuntu/expression/icgc_rnaseq/star_align.py',
                      help='path to star pipeline')
    star.add_argument('--input_dir', default='/home/ubuntu/SCRATCH', required=True, help='parent path for all datasets')
    star.add_argument('--genome_fasta_file', type=str, help='path to reference genome', required=True
                default='/home/ubuntu/SCRATCH/GRCh38.d1.vd1.fa')
    star.add_argument('--quantMode', type=str, default="", help='enable transcriptome mapping in STAR')

    cufflinks = parser.add_argument_group("cufflinks pipeline")
    cufflinks.add_argument('--cufflinks_pipeline', type=str,
                            default='/home/ubuntu/expression/compute_expression.py')
    args = parser.parse_args()

    analysis_id = args.analysis_id

    workdir = os.path.join(args.input_dir, analysis_id)

    if not os.path.isdir(workdir):
        raise Exception("Cannot locate analysis_id %s" %analysis_id)

    if not os.path.isdir(args.genome_dir):
        raise Exception("Cannot locate STAR genome build: %s" %args.genome_dir)

    if not os.path.isfile(args.genome_fasta_file):
        raise Exception("Cannot locate Genome FASTA File: %s" %args.genome_fasta_file)

    if not os.path.isfile(args.gtf):
        raise Exception("Cannot locate GTF file: %s" %args.gtf)

    if os.path.isdir(workdir):
        star_log_file = "%s_star.log" %(os.path.join(args.input_dir, analysis_id, analysis_id))
        logger = setupLog.setup_logging(logging.INFO, analysis_id, star_log_file)
        run_pipeline(args, workdir, analysis_id, logger)
        #pipelineUtil.remove_dir(workdir)
