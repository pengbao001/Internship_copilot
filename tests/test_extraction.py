from app.extraction.skill_extractor import SkillExtractor
from app.ingestion.page_loader import PageLoader
from app.ingestion.text_cleaner import TextCleaner

loader = PageLoader()
cleaner = TextCleaner()
extractor = SkillExtractor()

document = loader.load_from_text(
    text="""
    We are looking for interns with experience in Python, pytorch,
    large language models, and retrieval-augmented generation.
    """
)

cleaned_text = cleaner.clean(document.raw_text, source_kind=document.source_kind)
result = extractor.extract(cleaned_text)

print(result.normalized_skills)
print(result.raw_matched_phrases)
print(result.phrases_by_skill)