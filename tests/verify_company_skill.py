import os
import shutil
from pathlib import Path
import sys

# Add project root to sys.path to ensure nanobot module is found
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from nanobot.company.loader import CompanyConfigLoader
except ImportError:
    # Fallback for when running from a different cwd context
    sys.path.append(str(Path.cwd()))
    from nanobot.company.loader import CompanyConfigLoader

def test_loading(scenario_name):
    print(f"\nScanning: {scenario_name}")
    workspace = Path("c:/Users/golde/code/Agent-company")
    loader = CompanyConfigLoader(workspace)
    loader.load_all()
    
    print(f"Loaded {len(loader.posts)} posts.")
    print(f"Loaded {len(loader.schemas)} schemas.")
    
    assert "Post_Tech_Analyst" in loader.posts, "Post_Tech_Analyst not found"
    assert "Doc_Task_Order" in loader.schemas, "Doc_Task_Order not found"
    print("Verification Successful!")

def main():
    skill_path = Path("c:/Users/golde/code/Agent-company/company/SKILL.md")
    bak_path = Path("c:/Users/golde/code/Agent-company/company/SKILL.md.bak")
    
    # Ensure starting clean: if .bak exists but .md doesn't, restore it first
    if bak_path.exists() and not skill_path.exists():
        print("Restoring initial state (found .bak, moving to .md)...")
        shutil.move(str(bak_path), str(skill_path))
    
    # Test 1: With SKILL.md
    try:
        test_loading("With SKILL.md")
    except Exception as e:
        print(f"Test 1 Failed: {e}")
        # If test 1 fails, we might still want to try test 2, but usually better to stop.
        # But let's verify if we should proceed.
        raise

    # Test 2: Without SKILL.md (Fallback)
    print("\nRenaming SKILL.md to SKILL.md.bak for fallback test...")
    if skill_path.exists():
        shutil.move(str(skill_path), str(bak_path))
    
    try:
        test_loading("Without SKILL.md (Fallback)")
    except Exception as e:
         print(f"Test 2 Failed: {e}")
         raise
    finally:
        # Restore
        if bak_path.exists():
            print("\nRestoring SKILL.md...")
            shutil.move(str(bak_path), str(skill_path))

if __name__ == "__main__":
    main()
