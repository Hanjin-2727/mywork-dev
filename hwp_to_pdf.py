#!/usr/bin/env python3
import os
import sys
import subprocess
import glob

def convert_hwp_to_pdf(input_path: str, output_dir: str = None) -> str:
    """
    Converts a .hwp or .hwpx file to PDF using LibreOffice in headless mode.
    
    :param input_path: Path to the .hwp or .hwpx file
    :param output_dir: Directory where the output PDF will be saved (defaults to same folder)
    :return: Path to the generated PDF file
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(input_path))
    
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        os.path.abspath(input_path),
        "--outdir", os.path.abspath(output_dir)
    ]
    
    print(f"Running conversion: {input_path} -> PDF ...")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Conversion failed: {result.stderr}")
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    return pdf_path

def convert_all_hwp_in_directory(directory_path: str):
    """Converts all .hwp and .hwpx files in a directory to PDF."""
    hwp_files = glob.glob(os.path.join(directory_path, "*.hwp")) + glob.glob(os.path.join(directory_path, "*.hwpx"))
    
    if not hwp_files:
        print(f"No .hwp or .hwpx files found in {directory_path}")
        return
        
    print(f"Found {len(hwp_files)} HWP file(s) to convert...")
    for file_path in hwp_files:
        try:
            pdf = convert_hwp_to_pdf(file_path)
            print(f"✅ Saved: {pdf}")
        except Exception as e:
            print(f"❌ Failed to convert {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isdir(target):
            convert_all_hwp_in_directory(target)
        else:
            convert_hwp_to_pdf(target)
    else:
        print("Usage:")
        print("  python3 hwp_to_pdf.py <file.hwp>")
        print("  python3 hwp_to_pdf.py <directory_with_hwp_files>")
