import shutil
from pathlib import Path
import sys

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from nanobot.company.loader import CompanyConfigLoader
except ImportError:
    # Fallback
    sys.path.append(str(Path.cwd()))
    from nanobot.company.loader import CompanyConfigLoader

def test_company_loading(name=None):
    print(f"\nScanning with name='{name}'...")
    workspace = Path("c:/Users/golde/code/Agent-company")
    loader = CompanyConfigLoader(workspace, company_name=name)
    loader.load_all()
    
    print(f"Base Path: {loader.base_path}")
    print(f"Loaded {len(loader.posts)} posts.")
    print(f"Loaded {len(loader.schemas)} schemas.")
    
    if name == "default" or name is None:
        assert "Post_Tech_Analyst" in loader.posts, "Post_Tech_Analyst not found in default"
    
    print("Verification Successful!")

def main():
    # 1. Test None (Legacy/Fallback or Default)
    # Be careful: if companies/default exists, it might pick that up instead of company/
    # In our migration we created companies/default, so it should resolve there if no name provided (per logic step 2)
    # Actually wait, logic step 2 says check companies/default. So None -> companies/default.
    try:
        test_company_loading(None)
    except Exception as e:
        print(f"Test None Failed: {e}")

    # 2. Test "default" explicitly
    try:
        test_company_loading("default")
    except Exception as e:
        print(f"Test 'default' Failed: {e}")

    # 3. Test "weather_report" (Empty but should find SKILL.md if we CREATE ONE)
    # Let's create a minimal SKILL.md for weather_report
    weather_dir = Path("c:/Users/golde/code/Agent-company/companies/weather_report")
    weather_dir.mkdir(parents=True, exist_ok=True)
    (weather_dir / "SKILL.md").write_text("---\nname: Weather Co\ncomponents:\n---\n")
    
    try:
        test_company_loading("weather_report")
    except Exception as e:
        print(f"Test 'weather_report' Failed: {e}")

if __name__ == "__main__":
    main()
