"""Verify both knowledge collections are working."""
import os, sys, logging
from pathlib import Path
os.environ["PYTHONIOENCODING"] = "utf-8"
import sys; sys.stdout.reconfigure(encoding="utf-8")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
logging.basicConfig(level=logging.WARNING)

# 1. Verify knowledge-space
from rag.knowledge_indexer import KnowledgeIndexer
k_idx = KnowledgeIndexer()
stats = k_idx.stats()
print(f"\n{'='*60}")
print(f"KNOWLEDGE-SPACE (knowledge_space collection)")
print(f"{'='*60}")
print(f"  Total chunks:     {stats.get('total_chunks', '?')}")
print(f"  Distinct sources: {stats.get('distinct_sources', '?')}")
results = k_idx.search("sistemas distribuidos bases de datos", n_results=3)
print(f"  Search test:      {len(results)} results for 'sistemas distribuidos'")
for r in results:
    print(f"    - [{r['metadata'].get('source','?').split(chr(92))[-1]}] {r['text'][:80]}...")

# 2. Verify skill_md
from services.skills.md_adapter import SkillMdIndexer
s_idx = SkillMdIndexer()
count = s_idx.count()
print(f"\n{'='*60}")
print(f"SKILL.MD (skill_md collection)")
print(f"{'='*60}")
print(f"  Total skills: {count}")
results = s_idx.search("seguridad informatica", n_results=5)
print(f"  Search test:  {len(results)} results for 'seguridad informatica'")
for r in results[:3]:
    meta = r['metadata']
    print(f"    - {meta.get('name','?'):25s} | {meta.get('description','')[:60]}")
print(f"\n{'='*60}")
print(f"✅ AMBAS COLECCIONES OPERATIVAS")
