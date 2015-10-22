import os
import logging
import subprocess
import pipelineUtil

def fastqc(fastqc_path, reads_1, reads_2, rg_id_dir, analysis_id, logger=None):
    """ perform pre-alignment qc checks using fastqc """

    if not os.path.isdir(rg_id_dir):
        raise Exception("Invalid directory: %s")

    fastqc_results = "%s" %(os.path.join(rg_id_dir, "fastqc_results"))
    if not os.path.isdir(fastqc_results):
        os.mkdir(fastqc_results)
    if not reads_2 == "":
        cmd = [fastqc_path, reads_1, reads_2, '--outdir', fastqc_results, '--extract']
    else:
        cmd = [fastqc_path, reads_1, '--outdir', fastqc_results, '--extract']
    exit_code = pipelineUtil.log_function_time("FastQC", analysis_id, cmd, logger)
    if not exit_code == 0:
        if not logger == None:
            logger.error('FastQC returned a non-zero exit code: %s' %exit_code)


