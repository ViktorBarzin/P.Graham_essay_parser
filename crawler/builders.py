import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle as PS
from config.settings.base import (MAIN_SITE,
                                  CHROME_DRIVER_PATH,
                                  PDF_NAME,
                                  PDF_CONTENT_STYLE,
                                  PDF_TITLE_STYLE,
                                  IN_PARAGRAPH_NEW_LINE_DISTANCE,
                                  DISTANCE_BETWEEN_PARAGRAPHS,
                                  DEBUG,
                                  EPUB_FILEPATH,
                                  EPUB_NAME,
                                  PDF_FILEPATH,
                                  PDF_META_AUTHOR,
                                  PDF_META_DOCUMENT_SUBJECT,
                                  PDF_META_DOCUMENT_CREATOR,
                                  AFTER_HEADING_DISTANCE,
                                  PDF_META_DOCUMENT_TITLE)


class MyDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'title_style':
                if hasattr(flowable, '_bookmarkName'):
                    bn = getattr(flowable, '_bookmarkName')
                else:
                    bn = None
                self.notify('TOCEntry', (0, text, self.page, bn))
                # print(text)
                # print(self.page)


class PdfBuilder:
    def __init__(self, filename, *, toc_style=PDF_TITLE_STYLE):
        self.filename = filename
        self.document = MyDocTemplate(self.filename)
        # Set metadata
        self.document.author = PDF_META_AUTHOR
        self.document.title = PDF_META_DOCUMENT_TITLE
        self.document.subject = PDF_META_DOCUMENT_SUBJECT
        self.document.creator = PDF_META_DOCUMENT_CREATOR

        self.toc = TableOfContents()
        self.toc.levelStyles = [
                PDF_CONTENT_STYLE,
                PS(fontSize=18, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=5, leading=12),
                ]
        self.parts = []
        self.toc_style = toc_style
        self._setup_toc()
        self.bad_essays = ['What You Can\'t Say', 'Revenge of the Nerds', 'Programming Bottom-Up']  # These essays notes section is not well formatted. Not gonna make links for them for now.


    def _setup_toc(self):
        toc_paragraph = Paragraph('Table of Contents', self.toc_style)
        self.parts.extend([toc_paragraph, self.toc, PageBreak()])

    def add_heading(self, text):
        heading = Paragraph(str(text) + '<a name="{0}" />'.format(text.as_lower_alpha_num()), PDF_TITLE_STYLE)
        heading._bookmarkName = text.as_lower_alpha_num()
        return heading

    def build(self, essay_titles_bodies):
        '''
        Responsible for building the pdf file
        essay_titles_bodies is a list of tuples in the format
        (essay_title, essay_body)
        '''
        for title, essay in essay_titles_bodies:
            # Draw title
            title = Title(title)

            #parts.append(Paragraph(title , PDF_TITLE_STYLE))
            self.parts.append(self.add_heading(title))
            self.parts.append(Spacer(1, AFTER_HEADING_DISTANCE))

            in_notes_section = False
            first_line = True

            # Split by \n\n to preserve essay formatting.
            for line in essay.split('\n\n'):

                if 'Notes' in line.strip():
                    # In notes section
                    in_notes_section = True

                # Write additional text before first line
                if first_line:
                    line = "Original Publication Date: " + line
                    first_line = False

                # Handle [1] for notes sections
                groups = re.findall(r'\[\d+\]', line)
                # One line may contain multiple note references eg. [1][2]
                if groups:
                    for group in groups:
                        note_number = re.search(r'\d+', group).group()
                        if in_notes_section:
                            # place link name only
                            line = line + '<a name="{0}_{1}" />'.format(title.as_lower_alpha_num(), note_number)
                        else:
                            # create a href to link
                            # TODO: Move those special essays
                            if str(title) in self.bad_essays:
                                # Notes section is different. Skip those for now
                                continue
                            line = line.replace(group, '') + '<a href="#{0}_{1}" textcolor="#0000FF">{2} </a>'.format(title.as_lower_alpha_num(), note_number, group)
                            # Add reverse link
                            # line = line + '<a name="{0}_{1}_back" />'.format(title, note_number)

                self.parts.append(Paragraph(line, PDF_CONTENT_STYLE))
                # New line between 'New lines' to preserve formatting
                self.parts.append(Spacer(1, IN_PARAGRAPH_NEW_LINE_DISTANCE))
            # Add TOC entry
            # toc.addEntry(0, title, 69)
            # Space between essays
            self.parts.append(Spacer(1, DISTANCE_BETWEEN_PARAGRAPHS))
            self.parts.append(PageBreak())
        # FFS multiBuild and build... fuck reportlab...
        self.document.multiBuild(self.parts)
        return len(self.parts)


class Title:
    '''
    Helper class to simplify operations with title names
    '''
    def __init__(self, text):
        self.title = text

    def as_lower_alpha_num(self):
        return re.sub(r'\W+', '_', self.title).lower()

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()
