import os
import argparse

def read_file(filename, data, header):
    sample_name = os.path.basename(filename).split(".")[0]
    fp = open(filename, "r")
    fp.readline()
    already_added = set()
    for line in fp:
        line.rstrip()
        line = line.split("\t")
        if len(line) == 13 :
            gene_name = line[4]
            scaled_estimate = "%f" %(float(line[9]))
            if gene_name not in data:
                data[gene_name] = list()
            if gene_name not in already_added:
                data[gene_name].append(scaled_estimate)
                already_added.add(gene_name)
    header.append(sample_name)
    return header, data


def convert_to_string(array):
    s = str()
    for i in xrange(len(array)):
        if i < len(array) - 1:
            s += "%s\t" %(array[i])
        else:
            s += array[i]
    return s

def write_to_file(header, data, dirname):
    f_out = open('%s' % os.path.join(dirname, "out.txt"), "w")
    f_out.write(convert_to_string(header))
    for gene in data:
        line = "\n%s\t%s" %(gene, convert_to_string(data[gene]))
        f_out.write(line)

def verify_all_genes(f, num_datasets):
    for line in f:
        line = line.split("\t")
        if len(line) != (num_datasets+1):
            print len(line)
    print "total_num_datasets: %d" %num_datasets

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='make_table.py')
    parser.add_argument('--dirname', default='/home/ubuntu/SCRATCH/lung_results')
    args = parser.parse_args()
    #dirname ="/Users/stuti/Data/gec22/breast_cancer/"
    header = list()
    data = dict()
    for subdir in os.listdir(args.dirname):
        subdir = os.path.join(args.dirname, subdir)
        if os.path.isdir(subdir):
            for filename in os.listdir(subdir):
                filename = os.path.join(subdir, filename)
                header, data = read_file(filename, data, header)
    #print header
    write_to_file(header, data, args.dirname)
    output = '%s' % os.path.join(args.dirname, "out.txt")
    o = open(output, "r")
    num_datasets = len(o.readline().split("\t"))
    #print "total_num_datasets: %d" %num_datasets
    verify_all_genes(o, num_datasets)
