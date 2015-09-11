import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='classify_brca_dataset.py')
    parser.add_argument('--dirname', default='/home/ubuntu/SCRATCH/lung_results')
    parser.add_argument('--label', help='file containing labels')
    parser.add_argument('--outdir', help='output directory')
    args = parser.parse_args()

    f = open(args.label, "r")
    d = dict()
    for line in f:
        line = line.split("\t")
        aa = line[0]
        lab = line[1].rstrip()
        d[aa] = lab

    for filename in os.listdir(args.dirname):
        aa = filename.split(".")[0]
        if aa in d:
            old_filename = "%s" %os.path.join(args.dirname, filename)
            new_filename = "%s" %os.path.join(args.outdir, d[aa], "BRCA_%s_%s" %(d[aa], aa))
            #print old_filename, new_filename
            os.system("mv %s %s" %(old_filename, new_filename))
