# sex4NGS
sex works for NGS data
# sex4NGS

The BAM Sex Prediction Tool is a Python script designed to extract chromosome counts from BAM files and predict the sex of samples based on these counts. It calculates the number of reads mapped to specific chromosomes (such as chr19, chrX, and chrY) and uses these numbers to determine the sex of the sample (XX or XY).

Features
Extracts read counts for specified chromosomes from BAM files.
Calculates ratios such as chrX/chr19, chrY/chr19, and chrY/chrX.
Predicts the sex of the sample based on the calculated ratios.
Merges results from multiple samples into a single summary file.

Ensure that you have samtools installed and available in your system's PATH. You can install samtools using your package manager or download it from the official website: Samtools.

Usage
Basic Usage:
```bash

python bam_sex_prediction.py --bam_list bam_files.txt --out_dir output_directory
Arguments
--bam_list: Path to a text file containing a list of BAM file paths (one per line).
--out_dir: Path to the directory where all results should be stored.
```

Example
Suppose you have a file named bam_files.txt with the following content:


/path/to/sample1.bam
/path/to/sample2.bam
You can run the tool as follows:

bash

python bam_sex_prediction.py --bam_list bam_files.txt --out_dir results
This will process each BAM file listed in bam_files.txt, generate individual summary files in the results directory, and merge them into a single sampleSummary.txt file.

Example
After running the tool, the sampleSummary.txt file will look like this:


sample    chr19    chrX    chrY    X/19    Y/19    Y/X    sex_prediction
sample1   891756   836918  714     0.9385  0.0008  0.0009  probable_XX
sample2   900000   450000  450000  0.5     0.5     1.0    probable_XY
Dependencies
Python 3.8+
samtools
argparse
subprocess
os
Contributing
Contributions are welcome! If you find any bugs or want to add new features, please open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
If you have any questions or need further assistance, feel free to contact us at:

Email: your-email@example.com
GitHub: yourusername
