from django.template import Context
from templatetags.artistsbytype import artistsbytype
import django.template.loader
import os,re,unicodedata


_FORMATS = {
    'whatcd':('whatcd.txt','what.cd'),
    'whatcd-tracks-only':('whatcd-tracks-only.txt','what.cd (tracks only)'),
    'wafflesfm':('wafflesfm.txt', 'waffles.fm'),
    'wafflesfm-tracks-only':('wafflesfm-tracks-only.txt', 'waffles.fm (tracks only)'),
    'plain':('plain.txt','plain'),
}

FORMAT_CHOICES = map(lambda x: (x,_FORMATS[x][1]),_FORMATS)
FORMAT_CHOICES.sort(lambda x,y: cmp(x[0],y[0]))

FORMAT_DEFAULT = 'whatcd'

FORMATS = _FORMATS.keys()


class FormatterValueError(ValueError):
    pass


class Formatter(object):
    
    def __init__(self,template_dir='output_formats'):
        self._template_dir = template_dir
    
    def format(self,data,format = FORMAT_DEFAULT):
        if not format:
            format = FORMAT_DEFAULT
        if not format in _FORMATS.keys():
            raise FormatterValueError
        t = django.template.loader.get_template(os.path.join(self._template_dir,_FORMATS[format][0]))
        #we render the description without autoescaping
        c = Context(data,autoescape=False)
        #t.render() returns a django.utils.safestring.SafeData instance which
        #would not be escaped if used in another template. We don't want that,
        #so create a plain unicode string from the return value
        return unicode(t.render(c))
    
    def get_filename(self,data):
        filename = u''
        if 'artists' in data:
            #get the names of the main artists
            artists = artistsbytype(data['artists'],"Main")
            filename += u', '.join(artists)
            if 'title' in data:
                filename += u' - '
        if 'title' in data:
            filename += data['title']
        unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore')
        return re.sub('[^\w\s-]', '', filename).strip()
    
    @staticmethod
    def get_valid_format(format):
        if not format in _FORMATS.keys():
            format = FORMAT_DEFAULT
        return format