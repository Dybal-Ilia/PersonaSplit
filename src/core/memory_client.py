import os
from typing import List, Optional, Sequence
import math
from dotenv import load_dotenv
from neo4j import GraphDatabase, basic_auth
from sentence_transformers import SentenceTransformer
from src.utils.logger import logger

load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI")
AURA_INSTANCE_ID = os.getenv("AURA_INSTANCE_ID")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIMS = int(os.getenv("EMBED_DIMS", "384"))

if not NEO4J_URI:
	if AURA_INSTANCE_ID:
		NEO4J_URI = f"neo4j+s://{AURA_INSTANCE_ID}.databases.neo4j.io"
	else:
		NEO4J_URI = "bolt://localhost:7687"


def _to_list(vec: Sequence[float]) -> List[float]:
	return [float(x) for x in vec]


class Neo4jMemory:
	def __init__(self):
		self._driver = GraphDatabase.driver(
			NEO4J_URI,
			auth=basic_auth(NEO4J_USER or "neo4j", NEO4J_PASSWORD or "neo4j"),
		)
		self._model = SentenceTransformer(EMBED_MODEL)
		try:
			with self._driver.session() as s:
				s.run("""
				CREATE CONSTRAINT IF NOT EXISTS FOR (m:Memory) REQUIRE m.id IS UNIQUE
				""")
				try:
					s.run(
						"""
						CREATE VECTOR INDEX memory_vec_idx IF NOT EXISTS
						FOR (m:Memory) ON (m.embedding)
						OPTIONS {
						  indexConfig: {
							`vector.dimensions`: $dims,
							`vector.similarity_function`: 'cosine'
						  }
						}
						""",
						dims=EMBED_DIMS,
					)
				except Exception as e2:
					logger.warning(f"Vector index DDL not applied (will fallback to client-side similarity): {e2}")
		except Exception as e:
			logger.warning(f"Neo4j schema init warning: {e}")

	def add(self, messages=None, user_id: Optional[str] = None, **kwargs):
		if isinstance(messages, dict):
			payload = messages
			messages = payload.get("messages", [])
			if user_id is None:
				user_id = payload.get("user_id")
		elif messages is None and kwargs:
			payload = next(iter(kwargs.values())) if len(kwargs) == 1 and isinstance(next(iter(kwargs.values())), dict) else kwargs
			if isinstance(payload, dict):
				messages = payload.get("messages", messages)
				if user_id is None:
					user_id = payload.get("user_id", user_id)

		if not messages:
			return

		if not isinstance(messages, list):
			messages = [messages]

		normalized = []
		for m in messages:
			if isinstance(m, str):
				normalized.append({"role": "user", "content": m})
			elif isinstance(m, dict):
				normalized.append(m)
		texts = [m.get("content", "") for m in normalized if m.get("content")]
		for text in texts:
			emb = self._model.encode(text)
			with self._driver.session() as s:
				s.run(
					"""
					MERGE (m:Memory {id: randomUUID()})
					SET m.text = $text,
						m.session_id = $session_id,
						m.embedding = $embedding,
						m.ts = timestamp()
					""",
					text=text,
					session_id=user_id or "default",
					embedding=_to_list(emb),
				)

	def search(self, query: str, user_id: Optional[str] = None, limit: int = 5, filters: Optional[dict] = None):
		session_id = user_id or (filters or {}).get("user_id") or "default"
		q_emb = _to_list(self._model.encode(query))
		with self._driver.session() as s:
			try:
				result = s.run(
					"""
					CALL db.index.vector.queryNodes('memory_vec_idx', $limit, $q_emb)
					YIELD node, score
					WHERE node.session_id = $session_id
					RETURN node.text AS text, score
					ORDER BY score DESC
					""",
					limit=limit,
					q_emb=q_emb,
					session_id=session_id,
				)
				rows = result.data()
				return [r["text"] for r in rows]
			except Exception as e:
				logger.warning(f"Vector index query failed, fallback to client-side similarity: {e}")
				result = s.run(
					"""
					MATCH (m:Memory {session_id: $session_id})
					RETURN m.text AS text, m.embedding AS emb
					ORDER BY m.ts DESC
					LIMIT $limit_fallback
					""",
					session_id=session_id,
					limit_fallback=max(limit * 10, 50),
				)
				rows = result.data()
		def cos_sim(a: List[float], b: List[float]) -> float:
			num = sum(x*y for x, y in zip(a, b))
			da = math.sqrt(sum(x*x for x in a))
			db = math.sqrt(sum(y*y for y in b))
			if da == 0 or db == 0:
				return -1.0
			return num / (da * db)
		scored = []
		for r in rows:
			emb = r.get("emb")
			if isinstance(emb, list) and emb:
				scored.append((r["text"], cos_sim(q_emb, [float(x) for x in emb])))
		scored.sort(key=lambda t: t[1], reverse=True)
		return [t[0] for t in scored[:limit]]


memory_client = Neo4jMemory()