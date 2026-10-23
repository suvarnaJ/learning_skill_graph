from src.queries import QUERIES


def test_has_at_least_ten_queries():
    assert len(QUERIES) >= 10


def test_includes_multihop_queries():
    assert "08_multihop_student_skill_company" in QUERIES
    assert "10_company_skill_match_multihop" in QUERIES


def test_queries_use_parameters_for_user_inputs():
    assert "$city" in QUERIES["04_students_by_city"]
    assert "$skill" in QUERIES["06_projects_using_skill"]
