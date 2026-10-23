"""CLI entry point: seed graph, demonstrate CRUD, run sample queries."""
from graph_db import LearningGraph
from queries import QUERIES


def show(title, rows):
    print(f"\n--- {title} ({len(rows)} row(s)) ---")
    for row in rows[:12]:
        print(row)
    if len(rows) > 12:
        print(f"... {len(rows) - 12} more rows")


def main():
    graph = LearningGraph()
    try:
        graph.create_constraints()
        counts = graph.seed_graph()
        print(f"Seeded graph: {counts['nodes']} nodes, "
              f"{counts['relationships']} relationships")

        # Run the query library. Each query is parameterized where it takes input.
        for name, query in QUERIES.items():
            params = {}
            if name == "04_students_by_city":
                params = {"city": "Pune"}
            elif name == "06_projects_using_skill":
                params = {"skill": "Python"}
            elif name == "08_multihop_student_skill_company":
                params = {"limit": 10}
            elif name == "09_recommend_courses_from_skill":
                params = {"student_id": "S1"}
            show(name, graph.run(query, **params))

        # CRUD demonstration with a temporary record, cleaned up at the end.
        demo_id = "S-DEMO"
        show("CREATE student", graph.create_student(demo_id, "Demo Student", "Pune"))
        show("CREATE enrollment", graph.enroll_student(demo_id, "C1"))
        show("READ / FILTER", graph.find_students_by_city("Pune"))
        show("UPDATE student", graph.update_student_city(demo_id, "Hyderabad"))
        show("DELETE relationship", graph.delete_enrollment(demo_id, "C1"))
        show("DELETE node", graph.delete_student(demo_id))

        final_counts = graph.count_graph()
        print("\nFinal seeded graph counts:", final_counts)
    finally:
        graph.close()


if __name__ == "__main__":
    main()
