from descgen.forms import InputForm,FormatForm
from descgen.formatter import FORMAT_DEFAULT
from descgen.scraper.factory import SCRAPER_DEFAULT

def add_forms(request):
    context = {
        'INPUT_FORM':InputForm(initial={'scraper':request.session.get("default_scraper", SCRAPER_DEFAULT)}),
        'FORMAT_FORM':FormatForm(initial={'description_format':request.session.get("default_format", FORMAT_DEFAULT)})
        }
    return context