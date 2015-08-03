from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def syntax_highlight(source, lang):
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = HtmlFormatter(linenos=True, lineanchors=True)
    result = highlight(source, lexer, formatter)
    return result
