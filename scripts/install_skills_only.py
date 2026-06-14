"""Install only garri333/Skills — same as install_knowledge_repos.py but just skills."""
import os, sys, logging
from pathlib import Path
os.environ["PYTHONIOENCODING"] = "utf-8"
import sys; sys.stdout.reconfigure(encoding="utf-8")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from services.skills.md_adapter import SkillMdIndexer
s_idx = SkillMdIndexer()
result = s_idx.install_repo("garri333/Skills")
print(f"   => {result}")
print(f"   Skills indexed: {s_idx.count()}")
