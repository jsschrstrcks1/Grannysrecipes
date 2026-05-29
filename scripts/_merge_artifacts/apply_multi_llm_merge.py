#!/usr/bin/env python3
"""
Hand-merge artifact for PR #27 (multi-llm-integration-plan, Grannysrecipes).

Surgically applies the new functionality from the multi-llm PR onto current
main: imports new skill directories, drops in supporting files, backs up +
replaces modified config. Does NOT auto-modify CLAUDE.md — prints a TODO
list of skill links to fold into the lean v2.0 hub.

WHAT THIS APPLIES (Grannysrecipes):
  New skills (15) — only those NOT already on main:
    accessibility-audit, careful-not-clever, consult, content-freshness,
    ebook-builder, icp-2, ingredient-substitution, link-integrity,
    nutrition-estimator, orchestra, orchestrate, recipe-story,
    recipe-transcription, recipe-validation, seo-schema-audit

  Skipped — already on main:
    cognitive-memory, session-checkpoint

  Supporting files (clean adds): bootstrap-env.sh, new-skills-proposal.md, skills-audit.md
  Config (with .bak): .claude/settings.json, .claude/skill-rules.json,
                       .claude/hooks/{image-safety-check,post-write-validate}.sh,
                       .gitignore (PR adds it)

NOT TOUCHED — handle manually:
  - CLAUDE.md: my v2.0 trim restructured it into a lean hub (with the
    Grannysrecipes-specific extracts: FRAGMENT_HANDLING, CONVERSIONS,
    NUTRITION_QUESTIONS, DUPLICATE_HANDLING, BLOAT_MANAGEMENT). Add
    references to the new skills under "Essential Reading" — script prints
    a suggested block at the end.

REQUIREMENTS:
  - Run from inside the Grannysrecipes repo on current main
  - PR #27 branch fetched: `git fetch origin claude/multi-llm-integration-plan-MZxEu`

HOW TO APPLY:
  cd <Grannysrecipes repo>
  git fetch origin claude/multi-llm-integration-plan-MZxEu
  python3 scripts/_merge_artifacts/apply_multi_llm_merge.py --dry-run
  python3 scripts/_merge_artifacts/apply_multi_llm_merge.py
  $EDITOR CLAUDE.md   # add suggested skills block
  git add .claude/ bootstrap-env.sh new-skills-proposal.md skills-audit.md .gitignore CLAUDE.md
  git commit -m "Merge PR #27: multi-llm + recipe skills (15 new)"
  # Then close PR #27 with comment linking to this commit.
"""

import shutil
import subprocess
import sys
from pathlib import Path

PR_HEAD_SHA = '345d0f03c947027b94e0e9318169f6174107e54f'
PR_BRANCH = 'claude/multi-llm-integration-plan-MZxEu'

NEW_SKILLS = [
    'accessibility-audit', 'careful-not-clever', 'consult',
    'content-freshness', 'ebook-builder', 'icp-2',
    'ingredient-substitution', 'link-integrity', 'nutrition-estimator',
    'orchestra', 'orchestrate', 'recipe-story',
    'recipe-transcription', 'recipe-validation', 'seo-schema-audit',
]

SUPPORTING_FILES = [
    'bootstrap-env.sh',
    'new-skills-proposal.md',
    'skills-audit.md',
]

MODIFIED_CONFIG = [
    '.claude/settings.json',
    '.claude/skill-rules.json',
    '.claude/hooks/image-safety-check.sh',
    '.claude/hooks/post-write-validate.sh',
    '.gitignore',
]


def git_path_exists_in_ref(ref: str, path: str) -> bool:
    return subprocess.run(
        ['git', 'cat-file', '-e', f'{ref}:{path}'],
        capture_output=True,
    ).returncode == 0


def checkout_from_ref(ref: str, path: str, repo_root: Path) -> bool:
    r = subprocess.run(
        ['git', 'checkout', ref, '--', path],
        cwd=repo_root, capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f'  ERROR checking out {path}: {r.stderr.strip()}', file=sys.stderr)
        return False
    return True


def main():
    dry = '--dry-run' in sys.argv
    repo_root = Path(__file__).resolve().parents[2]

    if not git_path_exists_in_ref(PR_HEAD_SHA, 'bootstrap-env.sh'):
        print(
            f'ERROR: PR head ({PR_HEAD_SHA[:8]}) not reachable.\n'
            f'  Did you fetch? git fetch origin {PR_BRANCH}',
            file=sys.stderr,
        )
        sys.exit(1)

    print(f'=== Importing skills from {PR_HEAD_SHA[:8]} ===')
    skills_added, skills_skipped = [], []
    for skill in NEW_SKILLS:
        target = repo_root / '.claude' / 'skills' / skill
        if target.exists():
            print(f'  SKIP {skill} (already on main)')
            skills_skipped.append(skill)
        elif dry:
            print(f'  [DRY] would import .claude/skills/{skill}/')
        else:
            if checkout_from_ref(PR_HEAD_SHA, f'.claude/skills/{skill}', repo_root):
                print(f'  + .claude/skills/{skill}')
                skills_added.append(skill)

    print(f'\n=== Supporting files ===')
    files_added, files_skipped = [], []
    for f in SUPPORTING_FILES:
        target = repo_root / f
        if target.exists():
            print(f'  SKIP {f} (already on main)')
            files_skipped.append(f)
        elif dry:
            print(f'  [DRY] would import {f}')
        else:
            if checkout_from_ref(PR_HEAD_SHA, f, repo_root):
                print(f'  + {f}')
                files_added.append(f)

    print(f'\n=== Modified config (backup + replace) ===')
    config_replaced, config_skipped = [], []
    for f in MODIFIED_CONFIG:
        target = repo_root / f
        if not git_path_exists_in_ref(PR_HEAD_SHA, f):
            print(f'  SKIP {f} (not in PR head)')
            config_skipped.append(f)
            continue
        backup = target.with_suffix(target.suffix + '.bak')
        if dry:
            print(f'  [DRY] would back up {f} -> {backup.name} and apply PR version')
        else:
            if target.exists() and not backup.exists():
                shutil.copy2(target, backup)
                print(f'  backup: {f} -> {backup.name}')
            if checkout_from_ref(PR_HEAD_SHA, f, repo_root):
                print(f'  ~ {f} (PR head version applied)')
                config_replaced.append(f)

    print(f'\n=== Summary ===')
    print(f'Skills added:      {len(skills_added)}')
    print(f'Skills skipped:    {len(skills_skipped)} (already on main)')
    print(f'Files added:       {len(files_added)}')
    print(f'Configs replaced:  {len(config_replaced)} (backups in *.bak)')

    if dry:
        print('\n[DRY RUN] No changes made.')
        return

    print(f'\n=== CLAUDE.md hand-edit ===')
    print('Add the following block to CLAUDE.md under "Essential Reading":')
    print()
    print('  | Skill | Purpose |')
    print('  |---|---|')
    for skill in skills_added or NEW_SKILLS:
        purpose = {
            'accessibility-audit': 'WCAG 2.1 AA pass on changed pages',
            'careful-not-clever': 'Integrity guardrail (active on every file mod)',
            'consult': 'Quick single-model second opinion',
            'content-freshness': 'Scan for stale content',
            'ebook-builder': 'Print-PDF / EPUB build pipeline',
            'icp-2': 'ICP-2 SEO/AEO standard for 2026',
            'ingredient-substitution': 'Substitute ingredients with safety/diet rules',
            'link-integrity': 'Internal link + anchor validator',
            'nutrition-estimator': 'Estimate nutrition from ingredient list',
            'orchestra': 'Fan-out + deliberation across LLMs',
            'orchestrate': 'Linear multi-LLM pipeline',
            'recipe-story': 'Recipe narrative voice',
            'recipe-transcription': 'OCR + transcription for handwritten recipes',
            'recipe-validation': 'Recipe JSON schema check',
            'seo-schema-audit': 'JSON-LD / Open Graph / Twitter Card validator',
        }.get(skill, '')
        print(f'  | `{skill}` | {purpose} |')

    print(f'\n=== Next steps ===')
    print('  git status                                   # review')
    print('  git diff --stat HEAD                         # summary')
    print('  $EDITOR CLAUDE.md                            # add the block above')
    print('  git add .claude/ bootstrap-env.sh new-skills-proposal.md skills-audit.md .gitignore CLAUDE.md')
    print('  git commit -m "Merge PR #27: multi-llm + recipe skills (15 new)"')
    print('  # Close PR #27 with link to this commit.')


if __name__ == '__main__':
    main()
