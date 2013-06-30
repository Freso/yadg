from celery.decorators import task

@task
def get_results(scraper, additional_data):
    return scraper.get_result(), additional_data