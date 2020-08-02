from pathlib import Path
import minecart
import os
import glob
from hocr_pdf import export_pdf
import shutil
from PIL import Image
import pyocr
import pyocr.builders
import codecs


class Converter():

    def __init__(self, input_file, clean_up=True, tesseract_path=None):
        self.input_file = input_file
        self.clean_up = clean_up
        self.temp_path = Path(self.input_file.split(".")[0])
        print(self.temp_path)

    def extract_images(self):
        """
        Extract all images from the pdf file
        """
        pdf_file = Path(self.input_file)
        doc = minecart.Document(open(pdf_file, 'rb'))

        # Creating temporary folder
        try:
            os.makedirs(self.temp_path)
        except OSError:
            print("Temporary directory already exists")
        else:
            print(
                "Successfully created the directory %s" % self.temp_path)
        # Extract images
        n_imgs = 0
        for p, page in enumerate(doc.iter_pages()):
            for i, im in enumerate(page.images):
                im.as_pil().save(self.temp_path / f"image_{p+1}.jpg")
                n_imgs += 1
            print(f"Extracting image {i+1} from page {p+1}")

        # Update images
        self.images = glob.glob(str(self.temp_path) + "/*.jpg")
        return n_imgs

    def perform_ocr(self, img):
        """
        Convert the images in text and save in the .hocr extension
        """
        # Extract HOCR
        tool = pyocr.get_available_tools()[0]
        builder = pyocr.builders.LineBoxBuilder()
        line_boxes = tool.image_to_string(
            Image.open(img),
            lang='eng',
            builder=builder
        )
        hocr_file = img.replace("jpg", "hocr")
        with codecs.open(hocr_file, 'w', encoding='utf-8') as file_descriptor:
            builder.write_file(file_descriptor, line_boxes)

        print(f"Performing OCR on image {img}")

    def create_output_file(self):
        """
        Create the output and cleans the temporary folder
        """
        # Merge files
        export_pdf(self.temp_path, 300, self.input_file.replace(
            ".pdf", "") + "_output.pdf", True)

        # Cleaning up directory
        print("Cleaning up")
        if self.clean_up:
            try:
                shutil.rmtree(self.temp_path)
            except OSError as e:
                print("Error: %s : %s" % (self.temp_path, e.strerror))

    def convert_searchable(self):
        """
        Perform all steps
        """
        self.extract_images()
        for img in self.images:
            self.perform_ocr(img)
        self.create_output_file()


if __name__ == "__main__":
    for pdf in ["test.pdf"]:
        converter = Converter()
        converter.convert_searchable()
