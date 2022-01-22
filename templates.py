#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2020, Ahmed Zaki <azaki00.dev@gmail.com>'
__docformat__ = 'restructuredtext en'

from functools import partial
from collections import OrderedDict, defaultdict
import re
import traceback
import copy
import json

# python3 compatibility
from six.moves import range
from six import text_type as unicode, string_types as basestring

from calibre import prints
from calibre.constants import DEBUG
from calibre.ebooks.metadata import MetaInformation
from calibre.ebooks.metadata.book.formatter import SafeFormat
from calibre.gui2 import error_dialog, question_dialog
from calibre.gui2.dialogs.template_dialog import TemplateDialog
from calibre.gui2.ui import get_gui

from .common_utils import get_icon

GUI = get_gui()

TEMPLATE_PREFIX = 'TEMPLATE: '
TEMPLATE_ERROR = 'TEMPLATE_ERROR: '

try:
    load_translations()
except NameError:
    pass

def check_template(template, show_error=False):
    db = GUI.current_db
    error_msgs = [
        TEMPLATE_ERROR,
        'unknown function',
        'unknown identifier',
        'unknown field',
        'assign requires the first parameter be an id',
        'missing closing parenthesis',
        'incorrect number of arguments for function',
        'expression is not function or constant'
    ]
    try:
        book_id = list(db.all_ids())[0]
        mi = db.get_metadata(book_id, index_is_id=True, get_user_categories=True)
    except:
        mi = MetaInformation(_('Unknown'))
    
    output = SafeFormat().safe_format(template, mi, TEMPLATE_ERROR, mi)
    for msg in error_msgs:
        if output.lower().find(msg.lower()) != -1:
            error = output.lstrip(TEMPLATE_ERROR)
            if show_error:
                error_dialog(GUI, _('Template Error'),
                        _('Running the template returned an error:') +'\n'+ str(error),
                        show=True)
            return error
    return True


class TemplateBox(TemplateDialog):
    def __init__(self, parent=None, template_text=''):
        self.db = GUI.current_db
        self.template = template_text
        if not parent: parent = GUI
        
        rows = GUI.current_view().selectionModel().selectedRows()
        if rows:
            index = rows[0]
            mi = self.db.get_metadata(index.row(), index_is_id=False, get_cover=False)
        else:
            try:
                book_id = list(self.db.all_ids())[0]
                mi = self.db.get_metadata(book_id, index_is_id=True, get_user_categories=True)
            except:
                mi = MetaInformation(_('Unknown'))
        ## add any extra fields by actions that define update_metadata
        
        if not template_text:
            text = _('Enter a template to test using data from the selected book')
            text_is_placeholder = True
        else:
            text = None
            text_is_placeholder = False
         
        TemplateDialog.__init__(self, parent, text, mi=mi, text_is_placeholder=text_is_placeholder)
        self.setWindowTitle(_('Template editor'))
        if template_text:
            self.textbox.insertPlainText(template_text)
    
    def template_is_valide(self):
        return check_template(self.template) is True
    
    def accept(self):
        self.template = unicode(self.textbox.toPlainText()).rstrip()
        TemplateDialog.accept(self)

