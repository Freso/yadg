from descgen.forms import InputForm,FormatForm

def add_forms(request):
    return {'INPUT_FORM':InputForm(),'FORMAT_FORM':FormatForm()}