from descgen.forms import InputForm,FormatForm
from descgen.formatter import FORMAT_DEFAULT, Formatter
from descgen.scraper.factory import SCRAPER_DEFAULT, ScraperFactory

def add_forms(request):
    context = {
        'INPUT_FORM':InputForm(initial={'scraper':ScraperFactory.get_valid_scraper(request.session.get("default_scraper", SCRAPER_DEFAULT))}),
        'FORMAT_FORM':FormatForm(initial={'description_format':Formatter.get_valid_format(request.session.get("default_format", FORMAT_DEFAULT))})
        }
    return context