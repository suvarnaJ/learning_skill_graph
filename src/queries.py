"""Ten meaningful parameterized Cypher queries for the Learning & Skill Graph."""

QUERIES = {
    "01_students_and_courses": """
        MATCH (s:Student)-[:ENROLLED_IN]->(c:Course)
        RETURN s.name AS student, c.title AS course ORDER BY student
    """,
    "02_courses_and_skills": """
        MATCH (c:Course)-[:TEACHES_SKILL]->(sk:Skill)
        RETURN c.title AS course, collect(sk.name) AS skills ORDER BY course
    """,
    "03_mentors_and_courses": """
        MATCH (m:Mentor)-[:TEACHES]->(c:Course)
        RETURN m.name AS mentor, c.title AS course ORDER BY mentor
    """,
    "04_students_by_city": """
        MATCH (s:Student) WHERE toLower(s.city) = toLower($city)
        RETURN s.id AS id, s.name AS name, s.city AS city ORDER BY name
    """,
    "05_students_and_projects": """
        MATCH (s:Student)-[:BUILT]->(p:Project)
        RETURN s.name AS student, p.title AS project, p.status AS status
        ORDER BY student
    """,
    "06_projects_using_skill": """
        MATCH (p:Project)-[:USES]->(sk:Skill)
        WHERE toLower(sk.name) = toLower($skill)
        RETURN p.title AS project, sk.name AS skill ORDER BY project
    """,
    "07_company_interests": """
        MATCH (s:Student)-[:INTERESTED_IN]->(co:Company)
        RETURN co.name AS company, collect(s.name) AS interested_students
        ORDER BY company
    """,
    "08_multihop_student_skill_company": """
        MATCH (s:Student)-[:ENROLLED_IN]->(c:Course)-[:TEACHES_SKILL]->(sk:Skill)
        MATCH (s)-[:INTERESTED_IN]->(co:Company)
        RETURN s.name AS student, c.title AS course, sk.name AS skill,
               co.name AS company ORDER BY student LIMIT $limit
    """,
    "09_recommend_courses_from_skill": """
        MATCH (s:Student {id: $student_id})-[:ENROLLED_IN]->(:Course)
              -[:TEACHES_SKILL]->(sk:Skill)
        MATCH (recommended:Course)-[:TEACHES_SKILL]->(sk)
        WHERE NOT (s)-[:ENROLLED_IN]->(recommended)
        RETURN DISTINCT recommended.title AS recommended_course,
               collect(DISTINCT sk.name) AS shared_skills
        ORDER BY recommended_course
    """,
    "10_company_skill_match_multihop": """
        MATCH (s:Student)-[:BUILT]->(p:Project)-[:USES]->(sk:Skill)
        MATCH (s)-[:INTERESTED_IN]->(co:Company)
        RETURN s.name AS student, co.name AS company,
               collect(DISTINCT sk.name) AS demonstrated_skills
        ORDER BY student, company
    """,
    "11_mentor_skill_path": """
        MATCH (m:Mentor)-[:TEACHES]->(c:Course)-[:TEACHES_SKILL]->(sk:Skill)
        RETURN m.name AS mentor, c.title AS course, collect(sk.name) AS skills
        ORDER BY mentor
    """,
    "12_skill_demand": """
        MATCH (p:Project)-[:USES]->(sk:Skill)
        RETURN sk.name AS skill, count(p) AS project_count
        ORDER BY project_count DESC, skill
    """,
}
