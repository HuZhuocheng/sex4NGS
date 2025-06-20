import argparse
import subprocess
import os

class ReadsMapped:
    def __init__(self, bam_path, chr, bam_subset_path, bam_stats):
        self.bam_path = bam_path
        self.chr = chr
        self.bam_subset_path = bam_subset_path
        self.bam_stats = bam_stats

    def subset_bam_by_chr(self):
        command_line = f"samtools view -b {self.bam_path} {self.chr} > {self.bam_subset_path}"
        subprocess.check_output(command_line, shell=True)

    def compute_bam_stats(self):
        command_line = f"samtools stats {self.bam_subset_path} | grep ^SN | cut -f 2- > {self.bam_stats}"
        subprocess.check_output(command_line, shell=True)

    def return_reads_mapped(self):
        with open(self.bam_stats, "r") as f:
            for line in f:
                if line.startswith("reads mapped and paired"):
                    return line.rstrip("\n").split("\t")[1]
        return "0"

def classify_sex(X_19_ratio, Y_19_ratio, Y_X_ratio):
    """
    This function roughly classifies sex based on reads mapped ratio between X and 19, Y and 19, and Y and X
    :param X_19_ratio:
    :param Y_19_ratio:
    :param Y_X_ratio:
    :return: either "male" or "female"
    """
    if X_19_ratio >= 0.5 and Y_19_ratio <= 0.01 and Y_X_ratio <= 0.01:
        return "probable_XX"
    else:
        return "probable_XY"

def process_bam(bam_path, out_dir, sample_name):
    # Create output directories if they don't exist
    sample_dir = os.path.join(out_dir, sample_name)
    os.makedirs(sample_dir, exist_ok=True)

    outfile_path = os.path.join(sample_dir, f"{sample_name}_summary.tsv")
    with open(outfile_path, "w") as outfile:
        # Initialize the header
        header = ["sample", "chr19", "chrX", "chrY", "X/19", "Y/19", "Y/X", "sex_prediction"]
        print("\t".join(header), file=outfile)

        # Initialize the output row
        out = [sample_name]

        chr_list = ["chr19", "chrX", "chrY"]
        counts = {}
        for chrom in chr_list:
            bam_subset_path = os.path.join(sample_dir, f"{chrom}_bam_subset.bam")
            bam_stat = os.path.join(sample_dir, f"{chrom}_bam_stat.txt")
            reads_mapped = ReadsMapped(bam_path, chrom, bam_subset_path, bam_stat)
            reads_mapped.subset_bam_by_chr()
            reads_mapped.compute_bam_stats()
            count = reads_mapped.return_reads_mapped()
            counts[chrom] = count

            # Remove intermediate files (bam subsetted)
            os.remove(bam_subset_path)

        # Extract counts
        chr19_count = counts.get("chr19", "0")
        chrX_count = counts.get("chrX", "0")
        chrY_count = counts.get("chrY", "0")

        # Calculate ratios
        try:
            X_19_ratio = float(chrX_count) / float(chr19_count)
            Y_19_ratio = float(chrY_count) / float(chr19_count)
            Y_X_ratio = float(chrY_count) / float(chrX_count)
        except ZeroDivisionError:
            X_19_ratio = 0.0
            Y_19_ratio = 0.0
            Y_X_ratio = 0.0

        # Classify sex
        sex_pred = classify_sex(X_19_ratio, Y_19_ratio, Y_X_ratio)

        # Prepare output row
        out.extend([chr19_count, chrX_count, chrY_count, 
                    f"{X_19_ratio:.4f}", f"{Y_19_ratio:.4f}", f"{Y_X_ratio:.4f}", sex_pred])
        print("\t".join(out), file=outfile)

def merge_summaries(out_dir, summary_file):
    # Find all summary files
    summary_files = []
    for root, dirs, files in os.walk(out_dir):
        for file in files:
            if file.endswith("_summary.tsv"):
                summary_files.append(os.path.join(root, file))

    if not summary_files:
        print("No summary files found to merge.")
        return

    # Read and merge contents
    with open(summary_file, "w") as outfile:
        first_file = True
        for summary in summary_files:
            with open(summary, "r") as infile:
                lines = infile.readlines()
                if first_file:
                    # Write header only once
                    outfile.write(lines[0])
                    first_file = False
                # Write the rest of the lines
                outfile.writelines(lines[1:])
    print(f"Summaries merged into {summary_file}")

def main(args):
    with open(args.bam_list, 'r') as f:
        bam_files = [line.strip() for line in f if line.strip()]

    for bam_path in bam_files:
        sample_name = os.path.basename(bam_path).replace('.bam', '')
        process_bam(bam_path, args.out_dir, sample_name)

    print("all samples processed, waiting merge.")
    # Merge all summary files into one
    summary_file = os.path.join(args.out_dir, "sampleSummary.txt")
    merge_summaries(args.out_dir, summary_file)

def parse_args():
    parser = argparse.ArgumentParser(description="Process a list of BAM files to compute chromosome counts and sex prediction.")
    parser.add_argument("--bam_list", required=True, help="Path to the text file containing a list of BAM file paths.")
    parser.add_argument("--out_dir", required=True, help="Path to the directory where all results should be stored.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args)
