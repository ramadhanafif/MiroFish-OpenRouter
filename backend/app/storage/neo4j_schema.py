"""
Neo4j Schema — Cypher queries for index creation and schema management.

Called by Neo4jStorage._ensure_schema() to set up vector + fulltext indexes.
Vector index dimensions follow Config.EMBEDDING_DIMENSIONS; if an existing
index was created with a different dimension, the storage layer drops and
recreates it.
"""

# Constraints
CREATE_GRAPH_UUID_CONSTRAINT = """
CREATE CONSTRAINT graph_uuid IF NOT EXISTS
FOR (g:Graph) REQUIRE g.graph_id IS UNIQUE
"""

CREATE_ENTITY_UUID_CONSTRAINT = """
CREATE CONSTRAINT entity_uuid IF NOT EXISTS
FOR (n:Entity) REQUIRE n.uuid IS UNIQUE
"""

CREATE_EPISODE_UUID_CONSTRAINT = """
CREATE CONSTRAINT episode_uuid IF NOT EXISTS
FOR (ep:Episode) REQUIRE ep.uuid IS UNIQUE
"""

# Vector indexes (Neo4j 5.18+ for relationship vector indexes)
ENTITY_VECTOR_INDEX_NAME = "entity_embedding"
RELATION_VECTOR_INDEX_NAME = "fact_embedding"


def create_entity_vector_index(dimensions: int) -> str:
    return f"""
CREATE VECTOR INDEX {ENTITY_VECTOR_INDEX_NAME} IF NOT EXISTS
FOR (n:Entity) ON (n.embedding)
OPTIONS {{indexConfig: {{
    `vector.dimensions`: {int(dimensions)},
    `vector.similarity_function`: 'cosine'
}}}}
"""


def create_relation_vector_index(dimensions: int) -> str:
    return f"""
CREATE VECTOR INDEX {RELATION_VECTOR_INDEX_NAME} IF NOT EXISTS
FOR ()-[r:RELATION]-() ON (r.fact_embedding)
OPTIONS {{indexConfig: {{
    `vector.dimensions`: {int(dimensions)},
    `vector.similarity_function`: 'cosine'
}}}}
"""


# Fulltext indexes (for BM25 keyword search)
CREATE_ENTITY_FULLTEXT_INDEX = """
CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
FOR (n:Entity) ON EACH [n.name, n.summary]
"""

CREATE_FACT_FULLTEXT_INDEX = """
CREATE FULLTEXT INDEX fact_fulltext IF NOT EXISTS
FOR ()-[r:RELATION]-() ON EACH [r.fact, r.name]
"""

# Non-vector schema queries to run on startup
STATIC_SCHEMA_QUERIES = [
    CREATE_GRAPH_UUID_CONSTRAINT,
    CREATE_ENTITY_UUID_CONSTRAINT,
    CREATE_EPISODE_UUID_CONSTRAINT,
    CREATE_ENTITY_FULLTEXT_INDEX,
    CREATE_FACT_FULLTEXT_INDEX,
]


def all_schema_queries(dimensions: int) -> list:
    """All schema queries including dimension-aware vector indexes."""
    return STATIC_SCHEMA_QUERIES + [
        create_entity_vector_index(dimensions),
        create_relation_vector_index(dimensions),
    ]
