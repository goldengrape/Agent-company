from nanobot.agent.skills import SkillsLoader


def test_company_skills_are_discoverable(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)

    company_skills = tmp_path / "company_skills"
    (company_skills / "corp-only").mkdir(parents=True)
    (company_skills / "corp-only" / "SKILL.md").write_text(
        "# Corp Skill\n\nInternal guidance.",
        encoding="utf-8",
    )

    loader = SkillsLoader(workspace, company_skills_dir=company_skills)
    listed = loader.list_skills(filter_unavailable=False)

    names = {item["name"] for item in listed}
    assert "corp-only" in names

    content = loader.load_skill("corp-only")
    assert content is not None
    assert "Corp Skill" in content
