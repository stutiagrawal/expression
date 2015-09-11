import os

def remove_excess_slurm(dirname):
    """ remove slurm log files so that there is space for running more data """

    for filename in os.listdir(dirname):
        if filename.startswith("slurm"):
            filename = os.path.join(dirname, filename)
            if os.path.getsize(filename) > 7*(1024)^2:
                os.remove(filename)

remove_excess_slurm("/home/ubuntu/lung_study/brca_other")
