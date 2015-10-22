import os
import pipelineUtil
import argparse
import setupLog
import logging
import qc
import post_alignment_qc

def run_pipeline(args, workdir, analysis_id, fastq_dir, logger):
    """ align datasets using STAR and compute expression using cufflinks """

    for filename in os.listdir(workdir):
        if filename.endswith(".tar") or filename.endswith(".tar.gz"):
            tar_file_in = os.path.join(workdir, filename)
            break

    qc_dir = os.path.join(workdir, 'qc')
    if not os.path.isdir(qc_dir):
        os.mkdir(qc_dir)

    decompress(tar_file_in, fastq_dir)
    for fname in os.listdir(fastq_dir):
        if fname.endswith("_1.fastq.gz") or fname.endswith("_1.fastq"):
            reads_1 = os.path.join(fastq_dir, fname)
        if fname.endswith("_2.fastq.gz") or fname.endswith("_2.fastq"):
            reads_2 = os.path.join(fastq_dir, fname)
    qc.fastqc(args.fastqc_path, reads_1, reads_2, qc_dir, analysis_id, logger)

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

    exit_code = 1
    #Fix mate information for BAM
    exit_code, fix_mate_out = post_alignment_qc.fix_mate_information(args.picard, bam,
                                                                    analysis_id, workdir, logger)
    if exit_code == 0:
        os.remove(bam)
        assert(not os.path.isfile(bam))
        os.rename(fix_mate_out, bam)
        assert(os.path.isfile(bam))

    #validate the post alignment BAM file
    post_alignment_qc.validate_bam_file(args.picard, bam, analysis_id, qc_dir, logger)

    #collect RNA-seq metrics
    post_alignment_qc.collect_rna_seq_metrics(args.picard, bam, analysis_id,
                                                qc_dir, args.ref_flat, logger)

    #quantify using cufflinks
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

def decompress(filename, workdir):
    """ Unpack fastq files """

    if filename.endswith(".tar"):
        cmd = ['tar', 'xvf', filename, '-C', workdir]
    elif filename.endswith(".gz"):
        cmd = ['tar', 'xzvf', filename, '-C', workdir]
    else:
        raise Exception('Unknown input file extension for file %s' % filename)
    pipelineUtil.log_function_time("tar", filename, cmd)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='pipeline.py', description='STAR and cufflinks')
    parser.add_argument('--analysis_id', required=True, default=None, type=str, help='analysis ids')
    parser.add_argument('--gtf', required=True, type=str, help='genome annotation file')
    parser.add_argument('--p', type=str, default=1, help='number of threads')
    parser.add_argument('--picard', type=str, default='/home/ubuntu/bin/picard-tools-1.136/picard.jar',
                        help='path to picard binary')
    parser.add_argument('--ref_flat', required=True, type=str, default=None, help='path to refFlat file')
    parser.add_argument('--fastqc_path', type=str, default='/home/ubuntu/bin/FastQC/fastqc', help='path to fastqc binary')

    star = parser.add_argument_group("star pipeline")
    star.add_argument('--genome_dir', default='/home/ubuntu/SCRATCH/star_genome_d1_vd1_gtfv22/', required=True,
                     help='star index directory')
    star.add_argument('--star_pipeline', default='/home/ubuntu/expression/icgc_rnaseq/star_align.py',
                      help='path to star pipeline')
    star.add_argument('--input_dir', default='/home/ubuntu/SCRATCH', required=True, help='parent path for all datasets')
    star.add_argument('--genome_fasta_file', type=str, help='path to reference genome', required=True,
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
        fastq_dir = os.path.join(workdir, '%s_fastq_files' %analysis_id)
        if not os.path.isdir(fastq_dir):
            os.mkdir(fastq_dir)
        run_pipeline(args, workdir, analysis_id, fastq_dir, logger)
        #pipelineUtil.remove_dir(workdir)
