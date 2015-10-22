import pipelineUtil
import os
import subprocess

def validate_bam_file(picard_path, bam_file, uuid, outdir, logger=None):
   """ Validate resulting post-alignment BAM file """

   if os.path.isfile(picard_path) and os.path.isfile(bam_file):
        outfile = os.path.join(outdir, "%s.validate" %uuid)
        tmp_dir = os.path.join(outdir, 'tmp')
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)
        cmd = ['java', '-jar', picard_path, "ValidateSamFile", "I=%s" %bam_file,
               "O=%s" %outfile, "VALIDATION_STRINGENCY=LENIENT",
               "TMP_DIR=%s" %tmp_dir]
        exit_code = pipelineUtil.log_function_time("ValidateSAM", uuid, cmd, logger)
        if exit_code == 0:
            assert(os.path.isfile(outfile))
   else:
       raise Exception("Invalid path to picard or BAM")

   if not exit_code == 0:
       if not logger == None:
            logger.error("""
                        Picard ValidateSamFile command %s returned non-zero exit code %s
                        but continuting with metrics collection.
                        """
                        %(cmd, exit_code))

   return exit_code

def collect_rna_seq_metrics(picard_path, bam_file, uuid, outdir, ref_flat, logger=None):
    """ Collect RNA-seq metrics using Picard """

    if os.path.isfile(picard_path) and os.path.isfile(bam_file):
        tmp_dir = os.path.join(outdir, 'tmp')
        outfile = os.path.join(outdir, "%s.rna_seq_metrics.txt" %uuid)
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)
        cmd = ['java', '-jar', picard_path, "CollectRnaSeqMetrics", "METRIC_ACCUMULATION_LEVEL=READ_GROUP",
                "I=%s" %bam_file, "O=%s" %outfile, "STRAND=NONE",
                "REF_FLAT=%s" %ref_flat, "VALIDATION_STRINGENCY=LENIENT", "TMP_DIR=%s" %tmp_dir]
        exit_code = pipelineUtil.log_function_time("RNAseq_metrics", uuid, cmd, logger)
        if exit_code == 0:
            assert(os.path.isfile(outfile))
    else:
        raise Exception("Invalid path to picard or bam")

    if not exit_code == 0:
       if not logger == None:
            logger.error("Picard CollectRnaSeqMetrics returned non-zero exit code %s" %exit_code)
       raise Exception("Picard CollectRnaSeqMetrics command %s returned non-zero exit code %s" %(cmd, exit_code))

    return exit_code


def fix_mate_information(picard_path, bam_file, uuid, outdir, logger=None):
    """ Fix the mate information for BAM files """

    if os.path.isfile(picard_path) and os.path.isfile(bam_file):
        tmp_dir = os.path.join(outdir, 'tmp')
        outfile =  "%s.fix" %bam_file
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)
        cmd = ['java', '-jar', picard_path, 'FixMateInformation', 'I=%s' %bam_file, 'O=%s' %outfile,
                'VALIDATION_STRINGENCY=LENIENT', 'TMP_DIR=%s' %tmp_dir]
        exit_code = pipelineUtil.log_function_time('FixMateInformation', uuid, cmd, logger)
        if exit_code == 0:
            assert(os.path.isfile(outfile))
    else:
        raise Exception("Invalid path to picard %s or BAM %s" %(picard_path, bam_file))

    if not exit_code == 0:
        if not logger == None:
            logger.error("Picard FixMateInformation returned non-zero exit code %s" %exit_code)
        raise Exception("Picard FixMateInformation command %s returned non-zero exit code %s" %(cmd, exit_code))

    return exit_code, outfile


