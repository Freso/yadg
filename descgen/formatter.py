from django.template import Context
import django.template.loader
import os


_FORMATS = {
    'whatcd':('whatcd.txt','what.cd'),
    'whatcd-tracks-only':('whatcd-tracks-only.txt','what.cd (tracks only)'),
    'wafflesfm':('wafflesfm.txt', 'waffles.fm'),
    'wafflesfm-tracks-only':('wafflesfm-tracks-only.txt', 'waffles.fm (tracks only)'),
    'plain':('plain.txt','plain'),
    'bbcode-generic':('bbcode-generic.txt','BBCode (generic)'),
}

FORMAT_CHOICES = map(lambda x: (x,_FORMATS[x][1]),_FORMATS)
FORMAT_CHOICES.sort(lambda x,y: cmp(x[0],y[0]))

FORMAT_DEFAULT = 'whatcd'

FORMATS = _FORMATS.keys()


class FormatterValueError(ValueError):
    pass


class Formatter(object):

    release_title_template = 'release_title.txt'
    
    def __init__(self,template_dir='output_formats'):
        self._template_dir = template_dir

    def _render_template(self, template, data):
        #we render the description without autoescaping
        c = Context(data,autoescape=False)
        #t.render() returns a django.utils.safestring.SafeData instance which
        #would not be escaped if used in another template. We don't want that,
        #so create a plain unicode string from the return value
        return unicode(template.render(c))

    def format(self,data,format = FORMAT_DEFAULT):
        if not format:
            format = FORMAT_DEFAULT
        if not format in _FORMATS.keys():
            raise FormatterValueError
        t = django.template.loader.get_template(os.path.join(self._template_dir,_FORMATS[format][0]))
        return self._render_template(t, data)
    
    def get_release_title(self,data):
        t = django.template.loader.get_template(os.path.join(self._template_dir,self.release_title_template))
        return self._render_template(t, data)
    
    @staticmethod
    def get_valid_format(format):
        if not format in _FORMATS.keys():
            format = FORMAT_DEFAULT
        return format