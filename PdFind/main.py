from pathlib import Path
import pytesseract
import minecart
import os
import glob
import copy
from hocr_pdf import export_pdf
from tqdm import tqdm
import shutil
import logging


def convert_searchable(input_file, cleanup=False):
    """
    Convert the given pdf file to a searchable pdf.
    """
    logging.propagate = False
    logging.getLogger().setLevel(logging.ERROR)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pdf_file = Path(input_file)
    doc = minecart.Document(open(pdf_file, 'rb'))
    n_pages = len(list(copy.deepcopy(doc).iter_pages()))

    # Progress bar
    pbar = tqdm(total=n_pages + 1)
    # Creating temporary folder
    try:
        temp_path = Path("temp") / input_file.split(".")[0]
        os.mkdir(temp_path, 0o755)
    except OSError:
        pbar.set_description("Temporary directory already exists")
    else:
        pbar.set_description(
            "Successfully created the directory %s" % temp_path)
    pbar.update(1)

    # Extract images
    for p, page in enumerate(doc.iter_pages()):
        for i, im in enumerate(page.images):
            im.as_pil().save(temp_path / f"image_{p+1}.jpg")
        pbar.update(1)
        pbar.set_description(f"Extracting image {i+1} from page {p+1}")

    # Extract HOCR
    images = glob.glob(str(temp_path) + "/*.jpg")
    pbar.reset(total=len(images) + 11)
    for img in images:
        hocr = pytesseract.image_to_pdf_or_hocr(
            img, lang='por', extension='hocr')
        hocr_file = img.replace("jpg", "hocr")
        with open(hocr_file, "wb+") as f:
            f.write(hocr)
        pbar.update(1)
        pbar.set_description(
            f"Performing OCR on image {img}")

    # Merge files
    pbar.set_description("Merging output file")
    export_pdf(temp_path, 300, input_file.replace(
        ".pdf", "") + "_output.pdf", True)
    pbar.update(10)

    # Cleaning up directory
    pbar.set_description("Cleaning up")
    if cleanup:
        try:
            shutil.rmtree(temp_path)
        except OSError as e:
            print("Error: %s : %s" % (temp_path, e.strerror))
    pbar.update(1)
    pbar.close()


if __name__ == "__main__":
    # pdfs = glob.glob("*.pdf")
    pdfs = ["test.pdf"]
    for pdf in pdfs:
        convert_searchable(pdf, cleanup=True)
