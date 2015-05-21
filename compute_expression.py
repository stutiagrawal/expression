import os
import argparse
import logging
import pipelineUtil
import setupLog
import multiprocessing

def cufflinks_compute(args, logger=None):
    """ compute rna-seq expression using cufflinks """

    cmd = ['cufflinks']

    if args.multi_read_correct == 'True':
        cmd.append('--multi-read-correct')
    if args.frag_bias_correct == 'True':
        cmd.append('--frag-bias-correct')

    cmd += [
            '--GTF', args.gtf,
            '--output-dir', args.out,
            '--num-threads', str(args.p),
            args.bam
          ]
    print cmd
    pipelineUtil.log_function_time('cufflinks', args.analysis_id, cmd, logger)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="compute_expression.py", description="compute the gene expression")

    required = parser.add_argument_group('required')
    required.add_argument('--bam', type=str, default=None, required=True, help="input bam file")
    required.add_argument('--gtf', type=str, default='/home/ubuntu/SCRATCH/gencode.v22.annotation.gtf',
                        required=True, help="genome annotation file")
    required.add_argument('--analysis_id', type=str, default=None, required=True, help='analysis id')


    optional = parser.add_argument_group('optional')
    optional.add_argument('--out', type=str, default=os.getcwd(), help="output directory")
    optional.add_argument('--p', type=int, default=1, help="number of threads")

    cufflinks = parser.add_argument_group('cufflinks quantification parameters')
    cufflinks.add_argument('--multi_read_correct', type=str, default='False',
                            help="use rescue method for multi-reads")
    cufflinks.add_argument('--frag_bias_correct', type=str, default='False',
                            help="use bias correction - reference fasta required")
    cufflinks.add_argument('--library_type', type=str, default='fr-unstranded',
                            help="library prep used for input reads")
    args = parser.parse_args()

    #setup a logger
    log_file = "%s.log" % os.path.join(args.out, "cufflinks_%s" %args.analysis_id)

    logger = setupLog.setup_logging(logging.INFO, "cufflinks_%s" %args.analysis_id, log_file)

    #raise errors for invalid input
    if not(os.path.isfile(args.bam)) or not(os.path.isdir(args.out) or not(os.path.isfile(args.gtf))):
        raise Exception("Invalid input file or output directory")

    if (multiprocessing.cpu_count() < args.p or args.p < 1):
        args.p = 1
        print("Invalid number of cores, using default value 1")

    cufflinks_compute(args, logger)

