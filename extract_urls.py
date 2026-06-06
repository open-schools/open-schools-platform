import django
from django.conf import settings
from django.urls import get_resolver

def get_urls():
    resolver = get_resolver()
    urls = []
    
    def extract_urls(urlpatterns, prefix=""):
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                extract_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            elif hasattr(pattern, 'pattern'):
                callback_name = getattr(pattern.callback, '__name__', str(pattern.callback))
                if hasattr(pattern.callback, 'view_class'):
                    callback_name = pattern.callback.view_class.__name__
                urls.append(f"{prefix}{pattern.pattern} -> {callback_name}")
                
    extract_urls(resolver.url_patterns)
    with open('urls.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')

if __name__ == "__main__":
    get_urls()
