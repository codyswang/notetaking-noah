import time
from stitcher import Stitcher
import PIL
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sys

class PDFifier:
        '''
        Class that helps create a PDF
        from a stitcher.
        '''
        def __init__(self, path=None):
                # Initialize stitcher object and pdf object
                self.path = path
                if(path == None):
                    self.stitcher = None
                else:
                    self.stitcher = Stitcher(self.path)

        def makePDF(self, stitcher):
            # Runs the stitcher
            stitcher.stitch()
            quilt = stitcher.get_quilt()

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Left', leading=24, alignment=TA_LEFT))

            doc = SimpleDocTemplate("notes.pdf",pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)

            page_height, page_width = letter
            pdf = list()

            for patch in quilt:
                    # Adds image
                    path = patch.slide_path

                    im_height, im_width = PIL.Image.open(path).size

                    ratio = max(im_height/page_height, im_width/page_width)

                    im = Image(path, int(im_height/ratio)-1, int(im_width/ratio)-1)
                    pdf.append(im)

                    text = ""
                    first = True

                    for texts in patch.script:
                        for words in texts:
                            if(first):
                                first = False
                                text += words
                            else:
                                text += (" " + words)
                    text = '<font size="18"><br/><br/>%s</font>' %text
                    pdf.append(Paragraph(text, styles["Left"]))
                    pdf.append(PageBreak())
            doc.build(pdf)

if(__name__ == '__main__'):
        path = sys.argv[1]
        pdf = PDFifier(path=path)
        pdf.makePDF(pdf.stitcher)
