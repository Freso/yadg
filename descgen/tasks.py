from celery.decorators import task

@task
def get_result(scraper, additional_data):
    return scraper.get_result(), additional_data