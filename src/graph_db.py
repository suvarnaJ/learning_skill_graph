"""Neo4j access layer for the Learning & Skill Graph project."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class LearningGraph:
    """Reusable graph operations backed by Neo4j Aura or a local Neo4j instance."""

    def __init__(self) -> None:
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        if not all((uri, username, password)):
            raise RuntimeError(
                "Missing Neo4j configuration. Copy .env.example to .env and set credentials."
            )
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.driver.verify_connectivity()

    def close(self) -> None:
        self.driver.close()

    def run(self, query: str, **params: Any) -> list[dict[str, Any]]:
        records, _, _ = self.driver.execute_query(
            query, parameters_=params, database_=self.database
        )
        return [record.data() for record in records]

    def create_constraints(self) -> None:
        """Create uniqueness constraints for stable IDs."""
        queries = [
            "CREATE CONSTRAINT student_id IF NOT EXISTS FOR (n:Student) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT course_id IF NOT EXISTS FOR (n:Course) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT mentor_id IF NOT EXISTS FOR (n:Mentor) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (n:Skill) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (n:Company) REQUIRE n.id IS UNIQUE",
        ]
        for query in queries:
            self.run(query)

    def seed_graph(self) -> dict[str, int]:
        """Seed 60 nodes and 90 relationships; safe to rerun."""
        groups = [
            ("Student", [
                {"id": f"S{i}", "name": name, "city": city, "year": year}
                for i, (name, city, year) in enumerate([
                    ("Aarav", "Pune", 2), ("Diya", "Mumbai", 3), ("Kabir", "Delhi", 1),
                    ("Meera", "Bengaluru", 4), ("Ishaan", "Pune", 3), ("Anaya", "Chennai", 2),
                    ("Vivaan", "Hyderabad", 1), ("Sara", "Mumbai", 4), ("Arjun", "Delhi", 2),
                    ("Myra", "Pune", 1),
                ], start=1)
            ]),
            ("Course", [
                {"id": f"C{i}", "title": title, "level": level}
                for i, (title, level) in enumerate([
                    ("Python Foundations", "Beginner"), ("Data Analytics", "Intermediate"),
                    ("Graph Databases", "Intermediate"), ("Machine Learning", "Advanced"),
                    ("Cloud Engineering", "Intermediate"), ("Cybersecurity Basics", "Beginner"),
                    ("SQL for Analytics", "Beginner"), ("Applied NLP", "Advanced"),
                    ("Data Engineering", "Advanced"), ("Product Analytics", "Intermediate"),
                ], start=1)
            ]),
            ("Mentor", [
                {"id": f"M{i}", "name": name, "expertise": skill}
                for i, (name, skill) in enumerate([
                    ("Neha Rao", "Python"), ("Rahul Shah", "Analytics"),
                    ("Ananya Iyer", "Neo4j"), ("Vikram Das", "ML"),
                    ("Pooja Nair", "Cloud"), ("Karan Mehta", "Security"),
                    ("Sana Khan", "SQL"), ("Dev Patel", "NLP"),
                    ("Ritu Bose", "Data Engineering"), ("Amit Jain", "Product Analytics"),
                ], start=1)
            ]),
            ("Skill", [
                {"id": f"SK{i}", "name": name, "category": category}
                for i, (name, category) in enumerate([
                    ("Python", "Programming"), ("SQL", "Data"), ("Neo4j", "Databases"),
                    ("Data Visualization", "Analytics"), ("Machine Learning", "AI"),
                    ("Cloud", "Infrastructure"), ("Security", "Security"),
                    ("NLP", "AI"), ("ETL", "Data Engineering"), ("Experiment Design", "Analytics"),
                ], start=1)
            ]),
            ("Project", [
                {"id": f"P{i}", "title": title, "status": status}
                for i, (title, status) in enumerate([
                    ("Retail Sales Dashboard", "Completed"), ("Fraud Signal Explorer", "In Progress"),
                    ("Course Recommender", "Completed"), ("Demand Forecasting", "In Progress"),
                    ("Cloud Cost Monitor", "Planned"), ("Phishing Classifier", "Completed"),
                    ("Customer Feedback Miner", "In Progress"), ("Data Quality Pipeline", "Completed"),
                    ("Product Funnel Analysis", "Planned"), ("Skill Gap Analyzer", "In Progress"),
                ], start=1)
            ]),
            ("Company", [
                {"id": f"CO{i}", "name": name, "industry": industry}
                for i, (name, industry) in enumerate([
                    ("TechNova", "Technology"), ("DataWorks", "Analytics"),
                    ("GraphLabs", "Software"), ("AI Ventures", "Artificial Intelligence"),
                    ("CloudScale", "Cloud"), ("SecurePath", "Cybersecurity"),
                    ("MarketPulse", "Retail"), ("HealthMetric", "Healthcare"),
                    ("FinSight", "Finance"), ("BrightApps", "Software"),
                ], start=1)
            ]),
        ]
        # Labels are fixed allow-listed identifiers; all record values use parameters.
        for label, items in groups:
            self.run(
                f"UNWIND $items AS item MERGE (n:{label} {{id: item.id}}) SET n += item",
                items=items,
            )

        # 15 relationships per type x 6 types = 90.
        rel_groups = [
            ("Student", "Course", "ENROLLED_IN", [
                (f"S{i}", f"C{((i + j - 2) % 10) + 1}")
                for i in range(1, 11) for j in (1, 2)
            ][:15]),
            ("Mentor", "Course", "TEACHES", [
                (f"M{i}", f"C{i}") for i in range(1, 11)
            ] + [(f"M{i}", f"C{((i+2-1)%10)+1}") for i in range(1, 6)]),
            ("Course", "Skill", "TEACHES_SKILL", [
                (f"C{i}", f"SK{((i+j-2)%10)+1}")
                for i in range(1, 11) for j in (1, 2)
            ][:15]),
            ("Student", "Project", "BUILT", [
                (f"S{i}", f"P{i}") for i in range(1, 11)
            ] + [(f"S{i}", f"P{((i+2-1)%10)+1}") for i in range(1, 6)]),
            ("Project", "Skill", "USES", [
                (f"P{i}", f"SK{((i+j-2)%10)+1}")
                for i in range(1, 11) for j in (1, 2)
            ][:15]),
            ("Student", "Company", "INTERESTED_IN", [
                (f"S{i}", f"CO{i}") for i in range(1, 11)
            ] + [(f"S{i}", f"CO{((i+3-1)%10)+1}") for i in range(1, 6)]),
        ]
        for left, right, rel_type, pairs in rel_groups:
            self.run(
                f"""
                UNWIND $pairs AS pair
                MATCH (a:{left} {{id: pair[0]}})
                MATCH (b:{right} {{id: pair[1]}})
                MERGE (a)-[:{rel_type}]->(b)
                """,
                pairs=[list(p) for p in pairs],
            )

        counts = self.count_graph()
        return counts

    def count_graph(self) -> dict[str, int]:
        node_result = self.run("MATCH (n) RETURN count(n) AS count")
        rel_result = self.run("MATCH ()-[r]->() RETURN count(r) AS count")
        return {"nodes": node_result[0]["count"], "relationships": rel_result[0]["count"]}

    # CREATE
    def create_student(self, student_id: str, name: str, city: str) -> list[dict[str, Any]]:
        return self.run(
            "CREATE (s:Student {id: $id, name: $name, city: $city}) "
            "RETURN s.id AS id, s.name AS name, s.city AS city",
            id=student_id, name=name, city=city,
        )

    def enroll_student(self, student_id: str, course_id: str) -> list[dict[str, Any]]:
        return self.run(
            """
            MATCH (s:Student {id: $student_id})
            MATCH (c:Course {id: $course_id})
            MERGE (s)-[r:ENROLLED_IN]->(c)
            RETURN s.name AS student, c.title AS course, type(r) AS relationship
            """,
            student_id=student_id, course_id=course_id,
        )

    # READ / SEARCH
    def find_students_by_city(self, city: str) -> list[dict[str, Any]]:
        return self.run(
            """
            MATCH (s:Student)
            WHERE toLower(s.city) = toLower($city)
            RETURN s.id AS id, s.name AS name, s.city AS city
            ORDER BY s.name
            """,
            city=city,
        )

    def list_courses_and_skills(self) -> list[dict[str, Any]]:
        return self.run(
            """
            MATCH (c:Course)-[:TEACHES_SKILL]->(sk:Skill)
            RETURN c.title AS course, collect(sk.name) AS skills
            ORDER BY course
            """
        )

    # UPDATE
    def update_student_city(self, student_id: str, city: str) -> list[dict[str, Any]]:
        return self.run(
            """
            MATCH (s:Student {id: $student_id})
            SET s.city = $city
            RETURN s.id AS id, s.name AS name, s.city AS city
            """,
            student_id=student_id, city=city,
        )

    # DELETE
    def delete_enrollment(self, student_id: str, course_id: str) -> list[dict[str, Any]]:
        return self.run(
            """
            MATCH (:Student {id: $student_id})-[r:ENROLLED_IN]->
                  (:Course {id: $course_id})
            WITH collect(r) AS rels
            FOREACH (r IN rels | DELETE r)
            RETURN size(rels) AS deleted_relationships
            """,
            student_id=student_id, course_id=course_id,
        )

    def delete_student(self, student_id: str) -> list[dict[str, Any]]:
        return self.run(
            """
            MATCH (s:Student {id: $student_id})
            WITH collect(s) AS nodes
            FOREACH (n IN nodes | DETACH DELETE n)
            RETURN size(nodes) AS deleted_nodes
            """,
            student_id=student_id,
        )
