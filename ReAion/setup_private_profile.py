"""Create ignored local interview-data files from public templates."""
from pathlib import Path
import shutil
from app_paths import user_data_dir, PROJECT_DIR

BASE = PROJECT_DIR
DEST = user_data_dir()
FILES = ("candidate_profile", "answer_bank", "interview_guidance", "interviews")
for stem in FILES:
    target = DEST / (stem + (".md" if stem != "answer_bank" and stem != "interviews" else ".json"))
    source = BASE / (stem + ".example" + target.suffix)
    if not target.exists():
        shutil.copyfile(source, target)
        print("created", target.name)
    else:
        print("kept", target.name)
print("Private files are stored in", DEST, "and are outside the project tree.")
