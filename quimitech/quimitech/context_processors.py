from datetime import datetime

def year_context_processor(request):
    return {'year': datetime.now().year}
