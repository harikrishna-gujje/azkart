from .models import Category

def getlinks(request):
    categories = Category.objects.all()
    return dict(categories=categories)