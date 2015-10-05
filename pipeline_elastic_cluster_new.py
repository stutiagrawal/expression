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

    remote_bam_path = "%s_star.bam" % os.path.join(args.bucket, analysis_id, analysis_id)
    pipelineUtil.upload_to_cleversafe(logger, remote_bam_path, bam)


    cufflinks_cmd = ['time', '/usr/bin/time', 'python', args.cufflinks_pipeline,
                     '--bam', bam,
                     '--gtf', args.gtf,
                     '--analysis_id', analysis_id,
                     '--out', star_output_dir,
                     '--p', args.p,
                     '--multi_read_correct', 'True'
                    ]

    pipelineUtil.log_function_time("CUFFLINKS", analysis_id, cufflinks_cmd, logger)

    cuffout_genes_local = os.path.join(star_output_dir, "genes.fpkm_tracking")
    cuffout_genes_remote = os.path.join(args.bucket, "cufflinks", "star_gene", args.disease, "%s.genes.fpkm_tracking" %analysis_id)
    pipelineUtil.upload_to_cleversafe(logger, cuffout_genes_remote, cuffout_genes_local)

    cuffout_isoforms_local = os.path.join(star_output_dir, "isoforms.fpkm_tracking")
    cuffout_isoforms_remote = os.path.join(args.bucket, "cufflinks", "star_iso", args.disease, "%s.isoforms.fpkm_tracking" %analysis_id)
    pipelineUtil.upload_to_cleversafe(logger, cuffout_isoforms_remote, cuffout_isoforms_local)

    pipelineUtil.remove_dir(star_output_dir)


def download_missing_reference(args_input, remote_default, bucket):

    path = os.path.dirname(args_input)
    if not os.path.isdir(path):
        os.mkdir(path)
    pipelineUtil.download_from_cleversafe(None, os.path.join(bucket, remote_default), args_input)

def download_from_alt_source(bucket, config, analysis_id, input_dir):
    pipelineUtil.download_from_cleversafe(None, os.path.join(bucket, analysis_id), input_dir, config)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='pipeline.py', description='STAR and cufflinks')
    parser.add_argument('--analysis_id', required=True, default=None, type=str, help='analysis ids')
    parser.add_argument('--gtf', required=True, type=str, help='genome annotation file')
    parser.add_argument('--bucket', type=str, help='path to remote bucket')
    parser.add_argument('--p', type=str, default=1, help='number of threads')
    parser.add_argument('--disease', type=str, required=True, help='disease abbreviation')

    star = parser.add_argument_group("star pipeline")
    star.add_argument('--genome_dir', default='/home/ubuntu/SCRATCH/star_genome_d1_vd1_gtfv22/', help='star index directory')
    star.add_argument('--star_pipeline', default='/home/ubuntu/icgc_rnaseq_align/star_align.py',
                      help='path to star pipeline')
    star.add_argument('--input_dir', default='/home/ubuntu/SCRATCH', help='parent path for all datasets')
    star.add_argument('--genome_fasta_file', type=str, help='path to reference genome',
                default='/home/ubuntu/SCRATCH/GRCh38.d1.vd1.fa')
    star.add_argument('--quantMode', type=str, default="", help='enable transcriptome mapping in STAR')

    cufflinks = parser.add_argument_group("cufflinks pipeline")
    cufflinks.add_argument('--cufflinks_pipeline', type=str,
                            default='/home/ubuntu/lung_study/programs/compute_expression.py')
    args = parser.parse_args()

    analysis_id = args.analysis_id

    workdir = os.path.join(args.input_dir, analysis_id)

    if not os.path.isdir(workdir):
        pipelineUtil.download_from_cleversafe(None, os.path.join(args.bucket, analysis_id), args.input_dir,
                                              '/home/ubuntu/.s3cfg_cleversafe')

    if not os.path.isdir(workdir):
        download_from_alt_source('s3://tcga_cghub_protected', '/home/ubuntu/.s3cfg_cleversafe',
                                analysis_id, args.input_dir)
    if not os.path.isdir(workdir):
        download_from_alt_source('s3://tcga_cghub_protected_2', '/home/ubuntu/.s3cfg_cleversafe',
                                analysis_id, args.input_dir)
    if not os.path.isdir(workdir):
        download_from_alt_source('s3://tcga_cghub_protected_3', '/home/ubuntu/.s3cfg_cleversafe',
                                analysis_id, args.input_dir)
    if not os.path.isdir(workdir):
        download_from_alt_source('s3://tcga_cghub_protected', '/home/ubuntu/.s3cfg_ceph',
                                analysis_id, args.input_dir)

    if not os.path.isdir(workdir):
        raise Exception("Cannot locate analysis_id %s" %analysis_id)

    if not os.path.isdir(args.genome_dir):
        pipelineUtil.download_from_cleversafe(None, os.path.join(args.bucket, 'star_genome_d1_vd1_gtfv22'), args.input_dir)

    if not os.path.isfile(args.genome_fasta_file):
        default = "GRCh38.d1.vd1.fa"
        download_missing_reference(args.genome_fasta_file, default, args.bucket)

    if not os.path.isfile(args.gtf):
        default = "gencode.v22.annotation.gtf"
        download_missing_reference(args.gtf, default, args.bucket)

    if os.path.isdir(workdir):
        star_log_file = "%s_star.log" %(os.path.join(args.input_dir, analysis_id, analysis_id))
        logger = setupLog.setup_logging(logging.INFO, analysis_id, star_log_file)
        run_pipeline(args, workdir, analysis_id, logger)
        star_log_out = os.path.join(args.bucket, 'logs', args.disease, '%s.log' %analysis_id)
        pipelineUtil.upload_to_cleversafe(logger,star_log_out, star_log_file)
        pipelineUtil.remove_dir(workdir)
