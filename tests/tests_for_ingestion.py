from app.ingestion.page_loader import PageLoader
from app.ingestion.text_cleaner import TextCleaner

loader = PageLoader()
cleaner = TextCleaner()

doc = loader.load_from_text(
    text="""
    AI Internship
    
    Requirements:
    * Python
    * PyTorch
    * NLP
    """
)

# print("Raw:")
# print(doc)
# print("Cleaned:")
# print(cleaner.clean(doc.raw_text, source_kind=doc.source_kind))

doc = loader.load_from_url(url="https://careers.rivian.com/careers-home/jobs/27354?lang=en-us&iis=LinkedIn")
print("Raw:")
print(doc)
print("Cleaned:")
print(cleaner.clean(doc.raw_text, source_kind=doc.source_kind))

loader.load_from_url(url="https://this-domain-probably-does-not-exist.example")

loader.load_from_url(url="ftp://example.com/file.pdf")