## Lib Import
import numpy as np
import pandas as pd
import sys
import subprocess
import os.path
import tempfile
import errno
import shutil
import logging

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

## Local Import
import pybeagle.vcfparser.vcf as vcf
import pybeagle.ungzip as ungzip

def convert_g_to_beagle3(G,file_output_geno,file_output_marker):
    (n,m) = G.shape

    def nb_to_nc(nb):
        if nb == 0:
            return "A\tA"
        elif nb == 1:
            return "A\tC"
        elif nb == 2:
            return "C\tC"
        else:
            return "?\t?"

    with open(file_output_geno, 'w') as f:
        line = "I\t" + "id\t" +\
            "\t".join([str(val) for val in range(n) for _ in (0,1)])
        f.write(line + "\n")
        for j in range(m):
            marker_j = G[:,j]
            line = "M\t" + "rs" + str(j) + "\t" +\
              "\t".join(map(nb_to_nc, marker_j))
            f.write(line + "\n")

    with open(file_output_marker, 'w') as f:
        for j in range(m):
            line = "rs" + str(j) + "\t" + str(j) + "\tA" + "\tC"
            f.write(line + "\n")

def convert_beagle3_to_vcf(file_in_geno,file_in_marker,file_output,
                           path_beagle2vcf):
    line = "java -jar {0} 1 {1} {2} ? > {3}".format(
        path_beagle2vcf, file_in_marker, file_in_geno, file_output)
    logging.info(line)
    subprocess.call(line,shell=True)

def run_beagle(file_in,file_out,path_beagle, nthreads):
    if nthreads is None:
    	line = "java -Xmx1000m -jar {0} gt={1} out={2}".format(
        	path_beagle, file_in, file_out)
    else:
	line = "java -Xmx1000m -jar {0} gt={1} out={2}, nthreads={3}".format(
        	path_beagle, file_in, file_out, nthreads)

    logging.info(line)
    subprocess.call(line,shell=True)

def g_to_vcf(G, haploVCF,
             path_beagle, path_beagle2vcf, nthreads):
    try:
        tmp_dir = tempfile.mkdtemp(prefix='TmpBeagle')
        beagle_geno = os.path.join(tmp_dir,'geno_beagle.inp')
        beagle_marker = os.path.join(tmp_dir,'marker_beagle.inp')
        geno_vcf = os.path.join(tmp_dir,'geno.vcf')
        haplodir = os.path.dirname(haploVCF)
        haploname = os.path.splitext(haploVCF)[0]
        haplodir_name = os.path.join(haplodir,haploname)

        convert_g_to_beagle3(G, beagle_geno, beagle_marker)

        convert_beagle3_to_vcf(beagle_geno, beagle_marker, geno_vcf,
                               path_beagle2vcf)
        run_beagle(geno_vcf, haplodir_name, path_beagle, nthreads)
        ungzip.ungzip(haplodir_name + ".vcf.gz")
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
        
def haploVCF_to_matrix(haploVCF):
    res = []
    vcf_reader = vcf.VCFReader(open(haploVCF,'r'))
    for record in vcf_reader:
        hap = []
        for sample in record.samples:
            hap1j,hap2j = map(int,sample['GT'].split('|'))
            hap.append(hap1j)
            hap.append(hap2j)

        res.append(hap)

    return np.array(res).T

def beagle_phase(G, path_beagle, path_beagle2vcf, nthreads=None):
    try:
        tmp_dir = tempfile.mkdtemp(prefix='TmpResBeagle')
        file_res = os.path.join(tmp_dir,'res_haplo.vcf')

        g_to_vcf(G,file_res,path_beagle,path_beagle2vcf, nthreads)
        return haploVCF_to_matrix(file_res)
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
    
def main(args=None):
    print("* Module Beagle *")
    path_beagle = os.path.expanduser('~/these/softPhase/beagle/beagle.r1398.jar')
    path_beagle2vcf = os.path.expanduser('~/these/softPhase/beagle/beagle2vcf.jar')

    df_g = pd.read_pickle(os.path.expanduser("~/these/proto/geno_chr1_ceu.pck"))
    G = df_g.as_matrix()
    
    res = beagle_phase(G,path_beagle,path_beagle2vcf)
    return res
    
if __name__ =='__main__':
    main()

    
