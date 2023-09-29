from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from docx.shared import RGBColor, Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def initiate_driver() -> webdriver.Chrome:
    """Sets up and returns the Selenium Chrome webdriver"""
    options = Options()
    options.page_load_strategy = "eager"
    options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)

def format_document(doc):

    section = doc.sections[0]

    # Footer
    footer = section.footer
    style = doc.styles['Normal']
    font = style.font

    p = footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = p.add_run("Bulk Lyrics by MW Digital Development")
    run.font.name = 'Arial'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(120, 120, 120)

    # Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(1.27)
        section.bottom_margin = Cm(1.27)
        section.left_margin = Cm(1.27)
        section.right_margin = Cm(1.27)

    # Lyrics font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)
