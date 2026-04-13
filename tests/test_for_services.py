from app.models.internship import Internship
from app.models.profile import Profile
from app.services.matching_service import MatchingService, ProfileService


# profile = Profile(
#     full_name="Bob Boss",
#     resume_text="Python, PyTorch, SQL, Docker, large language models, RAG",
#     summary="Interested in AI systems and NLP.",
# )
#
# internship = Internship(
#     title="LLM Engineering Intern",
#     company_name="Example AI",
#     raw_description="""
#     Requirements:
#     - Python
#     - PyTorch
#     - SQL
#     - Docker
#
#     Preferred Qualifications:
#     - Retrieval-augmented generation
#     - LangChain
#     """,
#     cleaned_description="""
#     Requirements:
#     - Python
#     - PyTorch
#     - SQL
#     - Docker
#
#     Preferred Qualifications:
#     - Retrieval-augmented generation
#     - LangChain
#     """,
# )
#
# service = MatchingService()
# results = service.rank_internships(profile=profile, internships=[internship])
#
# print(results[0].fit_score)
# print(results[0].matched_required_skills)
# print(results[0].matched_preferred_skills)
# print(results[0].missing_skills)


def test_profile_service_extracts_skills() -> None:
    profile = Profile(
        full_name="Bob Boss",
        resume_text="Python, PyTorch, SQL, large language models",
        summary="Worked on retrieval-augmented generation.",
    )

    service = ProfileService()
    result = service.build_skill_profile(profile)

    assert "Python" in result.normalized_skills
    assert "PyTorch" in result.normalized_skills
    assert "LLMs" in result.normalized_skills
    assert "RAG" in result.normalized_skills
    print("Test_profile_service_extracts_skills:")
    print("All tests passed!")


def test_matching_service_builds_required_and_preferred_sections() -> None:
    internship = Internship(
        title="AI Intern",
        company_name="Example AI",
        raw_description="""
        Requirements:
        - Python
        - PyTorch
        - SQL

        Preferred Qualifications:
        - LangChain
        - Retrieval-augmented generation
        """,
        cleaned_description="""
        Requirements:
        - Python
        - PyTorch
        - SQL

        Preferred Qualifications:
        - LangChain
        - Retrieval-augmented generation
        """,
    )

    service = MatchingService()
    profile = service.build_internship_skill_profile(internship)

    assert profile.required_skills == ("Python", "PyTorch", "SQL")
    assert profile.preferred_skills == ("LangChain", "RAG")
    assert profile.section_strategy == "sectioned"
    print("Test_matching_service_builds_required_and_preferred_sections:")
    print("All tests passed!")

def test_matching_service_scores_match_explainably() -> None:
    profile = Profile(
        full_name="Ada Lovelace",
        resume_text="Python, PyTorch, SQL, Docker, RAG",
    )

    internship = Internship(
        title="LLM Intern",
        company_name="Example AI",
        raw_description="""
        Requirements:
        - Python
        - PyTorch
        - SQL
        - Docker

        Preferred Qualifications:
        - RAG
        - LangChain
        """,
        cleaned_description="""
        Requirements:
        - Python
        - PyTorch
        - SQL
        - Docker

        Preferred Qualifications:
        - RAG
        - LangChain
        """,
    )

    service = MatchingService()
    result = service.rank_internships(profile=profile, internships=[internship])[0]

    assert result.matched_required_skills == ("Python", "PyTorch", "SQL", "Docker")
    assert result.matched_preferred_skills == ("RAG",)
    assert result.missing_preferred_skills == ("LangChain",)
    assert result.fit_score == 85.0
    print("Test_matching_service_scores_match_explainably:")
    print("All tests passed!")

def test_matching_service_falls_back_when_no_sections_exist() -> None:
    internship = Internship(
        title="General ML Intern",
        company_name="Example AI",
        raw_description="We are looking for Python, PyTorch, SQL, and Docker experience.",
        cleaned_description="We are looking for Python, PyTorch, SQL, and Docker experience.",
    )

    service = MatchingService()
    profile = service.build_internship_skill_profile(internship)

    assert profile.section_strategy == "fallback_all_required"
    assert "Python" in profile.required_skills
    assert profile.preferred_skills == ()
    print("Test_matching_service_falls_back_when_no_sections_exist:")
    print("All tests passed!")

def main() -> None:
    test_profile_service_extracts_skills()
    test_matching_service_builds_required_and_preferred_sections()
    test_matching_service_scores_match_explainably()
    test_matching_service_falls_back_when_no_sections_exist()

if __name__ == "__main__":
    main()