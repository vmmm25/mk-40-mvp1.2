"""Install knowledge repos into JARVIS — knowledge-space + garri333/Skills."""
import os, sys, logging
from pathlib import Path
os.environ["PYTHONIOENCODING"] = "utf-8"
import sys; sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    # ── 1. Knowledge-Space ──────────────────────────────────────────────
    print("\n" + "="*70)
    print("📚 Installing AnastasiyaW/knowledge-space...")
    print("="*70)
    from rag.knowledge_indexer import KnowledgeIndexer
    k_idx = KnowledgeIndexer()
    result = k_idx.install_repo("AnastasiyaW/knowledge-space")
    print(f"   → {result}")
    stats = k_idx.stats()
    print(f"   Collection stats: {stats.get('total_chunks', '?')} chunks, "
          f"{stats.get('distinct_sources', '?')} sources")

    # ── 2. SKILL.md (garri333/Skills) ─────────────────────────────────
    print("\n" + "="*70)
    print("🔌 Installing garri333/Skills (SKILL.md)...")
    print("="*70)
    from services.skills.md_adapter import SkillMdIndexer
    s_idx = SkillMdIndexer()
    result = s_idx.install_repo("garri333/Skills")
    print(f"   → {result}")
    count = s_idx.count()
    print(f"   Skills indexed: {count}")

    # ── Summary ────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("✅ INSTALLATION COMPLETE")
    print("="*70)
    print()
    print(f"   knowledge-space chunks: {stats.get('total_chunks', '?')}")
    print(f"   skill_md entries:       {count}")
    print()
    print("JARVIS can now use:")
    print("   • search_knowledge     — search the knowledge-space articles")
    print("   • search_skill_md      — search for SKILL.md skills")
    print("   • install_knowledge_repo — install more knowledge repos")
    print("   • install_skill_md_repo  — install more SKILL.md repos")

if __name__ == "__main__":
    main()
