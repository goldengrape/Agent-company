import shutil
from pathlib import Path
import sys

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from nanobot.company.loader import CompanyConfigLoader
from nanobot.company.manager import CompanyManager

def test_default_post_config():
    print("\n--- Verifying Default Post Configuration ---")
    workspace = Path("c:/Users/golde/code/Agent-company")
    
    # 1. Weather Report Company
    print("\n[Weather Report]")
    loader = CompanyConfigLoader(workspace, company_name="weather_report")
    loader.load_all()
    print(f"Default Post: {loader.default_post}")
    print(f"Template: {loader.default_task_template and loader.default_task_template[:30]}...")
    
    assert loader.default_post == "Post_Weather_Analyst", "Weather default post mismatch"
    assert "Weather Analyst" in loader.default_task_template, "Weather template mismatch"
    
    # 2. News Summary Company
    print("\n[News Summary]")
    loader = CompanyConfigLoader(workspace, company_name="news_summary")
    loader.load_all()
    print(f"Default Post: {loader.default_post}")
    print(f"Template: {loader.default_task_template and loader.default_task_template[:30]}...")
    
    assert loader.default_post == "Post_Tech_Analyst", "News default post mismatch"
    assert "Tech News Analyst" in loader.default_task_template, "News template mismatch"

    print("\nSUCCESS: Default configuration loaded correctly.")

if __name__ == "__main__":
    test_default_post_config()
