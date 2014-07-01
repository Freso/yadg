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
        for template in Template.objects.all():
            clean = True
            cached = template.cached_dependencies_set()
            actual = template.dependencies_set()

            if cached != actual:
                self.stdout.write('Mismatch for template "%s" (%d):\n' % (template.name, template.pk))
                self.stdout.write('  is:\n')
                for templ in sorted(cmp_func, cached):
                    self.stdout.write('    %s (%d)' % (templ.name, templ.pk))
                self.stdout.write('  should be:\n')
                for templ in sorted(cmp_func, actual):
                    self.stdout.write('    %s (%d)' % (templ.name, templ.pk))
                self.stdout.write('\n\n')
                clean =False

            i += 1
            percent = (i / float(count))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                sys.stderr.write('%d%%\n\n' % last)


        if clean:
            self.stdout.write('No discrepancies detected.')
        else:
            self.stdout.write('There were discrepancies.')
            sys.exit(1)