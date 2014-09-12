from django.core.management.base import BaseCommand
from ...models import Template
import sys


def cmp_func(x, y):
    return cmp(x.name.lower(), y.name.lower())


class Command(BaseCommand):
    help = 'Checks if the cached dependency closures equate the actual dependencies.'

    def handle(self, *args, **options):
        count = Template.objects.all().count()
        i = 0
        last = 0
        clean = True
        for template in Template.objects.all():
            cached = template.cached_dependencies_set()
            actual = template.dependencies_set()

            if cached != actual:
                self.stdout.write('Mismatch for template "%s" (%d):\n' % (template.name, template.pk))
                self.stdout.write('  is:\n')
                if cached:
                    for templ in sorted(cached, cmp_func):
                        self.stdout.write('    * %s (%d)\n' % (templ.name, templ.pk))
                else:
                    self.stdout.write('    <empty>\n')
                self.stdout.write('  should be:\n')
                if actual:
                    for templ in sorted(actual, cmp_func):
                        self.stdout.write('    * %s (%d)\n' % (templ.name, templ.pk))
                else:
                    self.stdout.write('    <empty>\n')
                self.stdout.write('\n\n')
                clean = False

            i += 1
            percent = (i / float(count))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                sys.stderr.write('%d%%\n' % last)


        if clean:
            self.stdout.write('No discrepancies detected.')
        else:
            self.stdout.write('There were discrepancies.')
            sys.exit(1)