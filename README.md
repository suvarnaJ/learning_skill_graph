# Learning & Skill Graph (Python + Neo4j)

## Problem statement
Learning platforms need to connect learners, courses, mentors, skills, portfolio projects, and potential employers. A graph makes it possible to explore multi-hop learning journeys and recommend courses or identify skills that connect projects with companies.

This project seeds a learning-platform knowledge graph from Python and demonstrates CRUD operations and parameterized Cypher queries against Neo4j Aura or another Neo4j database. No graph records need to be created manually in the database UI.

## Graph model

### Node types
| Label | Example properties | Purpose |
|---|---|---|
| `Student` | `id`, `name`, `city`, `year` | Learners |
| `Course` | `id`, `title`, `level` | Learning content |
| `Mentor` | `id`, `name`, `expertise` | Course instructors |
| `Skill` | `id`, `name`, `category` | Skills taught or used |
| `Project` | `id`, `title`, `status` | Portfolio work |
| `Company` | `id`, `name`, `industry` | Potential employers |

### Relationship types
- `(Student)-[:ENROLLED_IN]->(Course)`
- `(Mentor)-[:TEACHES]->(Course)`
- `(Course)-[:TEACHES_SKILL]->(Skill)`
- `(Student)-[:BUILT]->(Project)`
- `(Project)-[:USES]->(Skill)`
- `(Student)-[:INTERESTED_IN]->(Company)`

The seed data defines 60 nodes (10 of each label) and 90 relationships (15 of each type). Node IDs have uniqueness constraints. The seeding uses `MERGE`, so rerunning it updates seeded properties and avoids duplicating the same seed relationships.

## Architecture
- `src/graph_db.py`: connection, constraints, seed data, CRUD methods, graph counts.
- `src/queries.py`: a library of 12 useful Cypher queries.
- `src/main.py`: CLI orchestration and demonstrations.
- `.env`: local credentials (never commit this file).
- `.env.example`: safe configuration template.
- `requirements.txt`: Python dependencies.

Flow: CLI (`main.py`) → graph access layer (`LearningGraph`) → Neo4j Python Driver → Neo4j Aura.

## Requirements
- Python 3.10+
- Git
- Neo4j Aura database or a reachable Neo4j server
- VS Code recommended

## Setup
1. Clone the repository:
   ```bash
   git clone <YOUR_GITHUB_REPOSITORY_URL>
   cd learning_skill_graph
   ```
2. Create and activate a virtual environment on Windows PowerShell:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env`, then set the actual credentials from your Neo4j Aura console:
   ```dotenv
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_actual_password
   NEO4J_DATABASE=neo4j
   ```
5. Run:
   ```bash
   python src/main.py
   ```

The script verifies connectivity, creates constraints, seeds the graph, runs 12 sample queries, demonstrates create/read/update/delete, removes its temporary demo node, and prints final graph counts.

## Example queries
The full query library is in `src/queries.py` and includes 12 queries:
1. Students and courses
2. Courses and skills
3. Mentors and courses
4. Students filtered by city
5. Students and projects
6. Projects using a specified skill
7. Company interests
8. Multi-hop student → course → skill plus company interests
9. Course recommendations from shared skills
10. Multi-hop student → project → skill plus company interest
11. Mentor → course → skill path
12. Skill demand across projects

Example multi-hop traversal:
```cypher
MATCH (s:Student)-[:ENROLLED_IN]->(c:Course)-[:TEACHES_SKILL]->(sk:Skill)
MATCH (s)-[:INTERESTED_IN]->(co:Company)
RETURN s.name AS student, c.title AS course, sk.name AS skill, co.name AS company
LIMIT $limit
```

Example parameterized filter:
```cypher
MATCH (s:Student)
WHERE toLower(s.city) = toLower($city)
RETURN s.id, s.name, s.city
```

## CRUD operations
The `LearningGraph` class exposes methods to:
- Create a student (`create_student`)
- Create an enrollment (`enroll_student`)
- Read and filter students (`find_students_by_city`)
- Update a student's city (`update_student_city`)
- Delete a relationship (`delete_enrollment`)
- Delete a node and its attached relationships (`delete_student`)

All data values are supplied through query parameters. Labels and relationship types are selected from fixed, source-controlled identifiers because Cypher parameters cannot stand in for schema identifiers.

## Inspect the graph
After seeding, use Neo4j's query interface only to inspect/visualize:
```cypher
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100
```
Verify counts:
```cypher
MATCH (n) RETURN count(n) AS nodes;
MATCH ()-[r]->() RETURN count(r) AS relationships;
```
Expected seeded graph: 60 nodes and 90 relationships.

## Git/GitHub workflow
Suggested commit history (make these commits as you implement; do not fabricate history):
1. `chore: initialize Python project structure`
2. `feat: add Neo4j connection and graph seed data`
3. `feat: add parameterized CRUD operations`
4. `feat: add multi-hop Cypher query library`
5. `docs: document graph model and setup`

Example feature branch workflow:
```bash
git switch -c feature/multihop-queries
# implement/edit src/queries.py and README.md
git add src/queries.py README.md
git commit -m "feat: add multi-hop learning graph queries"
git switch main
git merge --no-ff feature/multihop-queries
git push -u origin main
git push -u origin feature/multihop-queries
```

Never commit `.env`, passwords, or `.venv`. Check `git status` before each commit.

## Security and limitations
This is demonstration data, not a production recommendation system. Validate user input and apply authorization before exposing operations through a web service. Keep Aura credentials private and rotate them if accidentally exposed.
