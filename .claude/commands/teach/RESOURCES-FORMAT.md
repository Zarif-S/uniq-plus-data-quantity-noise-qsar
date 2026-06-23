# RESOURCES.md Format

`RESOURCES.md` is the curated set of trusted sources for this topic. Knowledge for explainers should be drawn from here, not from parametric guesses. Wisdom comes from the communities listed here.

## Structure

```md
# {Topic} Resources

## Knowledge

- [Book/Paper/Doc: _Title_ — Author(s)](https://actual-verified-url.com)
  What it covers and when to reach for it.

## Wisdom (Communities)

- [Community Name](https://actual-verified-url.com)
  Signal quality and best use case.

## Gaps

- {Area the mission needs but no good resource has been found yet}
```

## Rules

- **High-trust only.** Prefer primary sources, recognised experts, peer-reviewed work, and communities with strong moderation. If a resource is marketing dressed as education, leave it out.
- **Annotate every entry.** A bare link is useless in three months. Add one line: what it covers and when to reach for it.
- **Group by Knowledge / Wisdom.** Mirrors the philosophy in the main skill. It is fine for a resource to appear in only one group.
- **Surface gaps explicitly.** If no good resource exists for an area the mission needs, write a `## Gaps` section listing what is missing. This drives future search.
- **Prune ruthlessly.** A resource that turned out to be wrong, shallow, or off-mission should be removed, not buried. Better five sharp sources than thirty mediocre ones.
- **Record community preferences.** If the user has opted out of joining communities, note it here so future sessions don't keep proposing them.
- **Verify before adding.** Do not guess URLs or assume a resource exists. Fetch and confirm each link before writing it here.

## QSAR / Cheminformatics Bootstrap

For QSAR or cheminformatics topics, the following are the canonical starting points. Gather and verify URLs before adding — do not fabricate links.

**Knowledge — find and verify:**
- RDKit official documentation — primary reference for all RDKit usage
- DeepChem documentation and tutorials — ML on molecular data
- ChEMBL database docs — bioactivity data source and query API
- MoleculeNet benchmark paper (Wu et al., 2018) — standard benchmark datasets and baselines
- Tropsha et al. QSAR best practices paper — model validation and applicability domain
- Hansch & Leo (or equivalent foundational text) — classical QSAR theory
- An applicability domain review (e.g. Sheridan, Netzeva, or equivalent peer-reviewed source)

**Wisdom — find and verify:**
- RDKit mailing list or GitHub Discussions
- r/cheminformatics (assess moderation quality before adding)
- Any active Slack/Discord for open-source cheminformatics communities
