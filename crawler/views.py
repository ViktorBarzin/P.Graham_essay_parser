import re
from os import path
from ebooklib import epub
from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseBadRequest
from config.settings.base import (
                                  PDF_NAME,
                                  EPUB_FILEPATH,
                                  EPUB_NAME,
                                  PDF_FILEPATH,
                                  PDF_TOC_STYLE)

from .builders import PdfBuilder
from .services import setup_driver, get_essay_title_and_contents


def download_essays_view(request):
    # Drop all that is not post
    if request.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=['POST'])

    if request.POST.get('download_type') == 'pdf':
        # download as pdf
        if not path.exists(PDF_FILEPATH):
        # if True:
            build_pdf(get_essay_title_and_contents(setup_driver()))

        with open(PDF_FILEPATH, 'rb') as r:
            response = HttpResponse(r.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{0}"'.format(PDF_NAME)
            return response
    elif request.POST.get('download_type') == 'epub':
        # download as epub

        # Uncomment the following in prod
        if not path.exists(EPUB_FILEPATH):
        # if True:
            build_epub(get_essay_title_and_contents(setup_driver()))

        with open('essays.epub', 'rb') as r:
            response = HttpResponse(r.read(), content_type='application/epub+zip')
            response['Content-Disposition'] = 'attachment; filename="{0}"'.format('essays.epub')
            return response
    else:
        INVALID_FORM_MESSAGE = '''<h1>You tried to hack my site! I have sent your IP address which is {0} to the police
        and now they are on their way to arrest you. Have fun in jail script kiddie ;)</h1>'''.format(request.META.get('REMOTE_ADDR')) # Have some fun with people messing with source code
        return HttpResponseBadRequest(INVALID_FORM_MESSAGE)


def build_pdf(essay_titles_bodies):
    '''
    You can use the builder with anything that is a list of tuples in the format:
    (essay_title, essay_body)
    '''
    builder = PdfBuilder(filename=PDF_FILEPATH, toc_style=PDF_TOC_STYLE)
    builder.build(essay_titles_bodies)



def build_epub(essay_titles_bodies):
    book = epub.EpubBook()

    # set metadata
    book.set_identifier('id123456')
    book.set_title('Paul Graham Essays')
    book.set_language('en')

    book.add_author('Paul Graham')

    book.toc = []
    book.spine = ['nav']
    #for i in range(5):
    for title, essay in essay_titles_bodies:
        # title = essay_titles_bodies[i][0]
        # essay = essay_titles_bodies[i][1]

        chapter = epub.EpubHtml(title=title, file_name='{0}.xhtml'.format(title), lang='en')
        chapter.content = essay
        book.add_item(chapter)
        book.toc.append(epub.Link('{0}.xhtml'.format(title), title, title))

        # basic spine
        book.spine.append(chapter)

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(nav_css)
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    epub.write_epub(EPUB_FILEPATH, book, {})


# def build_epub_lib(essay_titles_bodies):

#     book = epub.EpubBook()

#     # set metadata
#     book.set_identifier('id123456')
#     book.set_title('Sample book')
#     book.set_language('en')

#     book.add_author('Author Authorowski')
#     book.add_author('Danko Bananko', file_as='Gospodin Danko Bananko', role='ill', uid='coauthor')

#     # create chapter
#     c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='hr')
#     c1.content=u'<h1>Intro heading</h1><p>Hi there</p>'

#     # add chapter
#     book.add_item(c1)

#     # define Table Of Contents
#     book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
#     (epub.Section('Simple book'),
#     (c1, ))
#     )

#     # add default NCX and Nav file
#     book.add_item(epub.EpubNcx())
#     book.add_item(epub.EpubNav())

#     # define CSS style
#     style = 'BODY {color: white;}'
#     nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

#     # add CSS file
#     book.add_item(nav_css)

#     # basic spine
#     book.spine = ['nav', c1]

#     # write to the file
#     epub.write_epub('test.epub', book, {})



