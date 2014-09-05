from django.template import Context
import django.template.loader
import os


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

    def title_from_ReleaseResult(self, release_result):
        t = django.template.loader.get_template(os.path.join(self._template_dir,self.release_title_template))
        return self._render_template(t, {'result': release_result})