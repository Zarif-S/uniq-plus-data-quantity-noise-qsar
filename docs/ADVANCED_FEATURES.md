# Advanced Documentation Features

This guide covers optional patterns for teams that need more sophisticated documentation management as their projects grow.

## 📍 Breadcrumbs

- **New to this framework?** → [README.md](../README.md) for overview
- **Looking for core templates?** → [Root CLAUDE.md](../CLAUDE.md), [ROADMAP.md](../ROADMAP.md), [PROJECT_PLAN.md](../PROJECT_PLAN.md)
- **Looking for examples?** → [examples/ml-workflow/](../examples/ml-workflow/)

---

## Quick Navigation

- [1. DOCS.md Index Pattern](#1-docsmd-index-pattern) - For projects with 10+ documented folders
- [2. PR Documentation Checklist](#2-pr-documentation-checklist) - For team collaboration
- [3. Documentation Debt Tracking](#3-documentation-debt-tracking) - For fast-paced development
- [4. Conflict Detection Patterns](#4-conflict-detection-patterns) - For multiple editors
- [5. Multi-Folder Strategy Guide](#5-multi-folder-strategy-guide) - For evolving project structures
- [6. Scheduled Retrospectives](#6-scheduled-retrospectives) - For continuous improvement

---

## 1. DOCS.md Index Pattern

### When to Use

- **Project size**: 10+ documented folders/modules
- **Team size**: 3+ developers regularly working in different areas
- **Complexity**: Multiple layers of subfolder CLAUDE.md files

### What It Solves

As projects grow, even with hierarchical CLAUDE.md files, navigation can become complex. A DOCS.md index provides a bird's-eye view of all documentation.

### Implementation

Create a `DOCS.md` file in your project root:

```markdown
# Documentation Index

Quick reference to all documentation in this project.

## Core Documentation

- **[README.md](README.md)** - Public-facing project overview
- **[CLAUDE.md](CLAUDE.md)** - Main entry point for AI agents, setup guide
- **[ROADMAP.md](ROADMAP.md)** - Strategic vision (quarters/years)
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Current sprint/iteration plans
- **[CHANGELOG.md](CHANGELOG.md)** - Feature and change history
- **[README.md](../README.md)** - Public-facing project overview and setup

## Architecture Documentation

### Data Pipelines
```
data/
├── ingestion/
│   └── CLAUDE.md ────────── Data sources, loading, validation
├── preprocessing/
│   └── CLAUDE.md ────────── Cleaning, normalization, transforms
└── features/
    └── CLAUDE.md ────────── Feature engineering, selection
```

### Models
```
models/
├── training/
│   └── CLAUDE.md ────────── Training loops, hyperparameters, checkpoints
├── evaluation/
│   └── CLAUDE.md ────────── Metrics, validation, error analysis
└── registry/
    └── CLAUDE.md ────────── Model versioning, MLflow/ZenML setup
```

### Experiments
```
experiments/
├── notebooks/
│   └── CLAUDE.md ────────── Notebook organization, EDA patterns
└── tracking/
    └── CLAUDE.md ────────── Experiment logs, reproducibility
```

## Specialized Documentation

- **[docs/API.md](docs/API.md)** - API reference and examples
- **[docs/SECURITY.md](docs/SECURITY.md)** - Security guidelines and threat model
- **[docs/PERFORMANCE.md](docs/PERFORMANCE.md)** - Performance benchmarks and optimization
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Navigation Tips

**Starting a new task?**
1. Check [CLAUDE.md](CLAUDE.md#-documentation-navigation) task routing table first
2. If task is in a specific module, jump directly to that module's CLAUDE.md
3. Use this index for cross-module work or architectural questions

**Last Updated**: 2025-01-31
```

### Best Practices

1. **Keep it visual**: ASCII trees are easier to scan than lists
2. **Add context**: Brief descriptions (5-10 words) after each link
3. **Update regularly**: Add to your Definition of Done checklist
4. **Link back**: Reference this index from root CLAUDE.md

---

## 2. PR Documentation Checklist

### When to Use

- **Team size**: 2+ developers submitting PRs
- **Change frequency**: Regular feature additions or architectural changes
- **Problem**: Documentation updates being forgotten

### What It Solves

Automates reminders to update documentation during code reviews, reducing documentation drift.

### Implementation

See [../.github/PULL_REQUEST_TEMPLATE/documentation.md](../.github/PULL_REQUEST_TEMPLATE/documentation.md) for the template.

**To use in your project**:

1. Copy `.github/PULL_REQUEST_TEMPLATE/documentation.md` to your repo
2. GitHub will automatically include this checklist in PRs
3. Reviewers can verify checklist completion before merging

**Checklist includes**:
- ROADMAP.md (strategic changes)
- PROJECT_PLAN.md (task completion)
- Root CLAUDE.md (setup/structure changes)
- Subfolder CLAUDE.md (architecture changes)
- CHANGELOG.md (user-facing features)
- Code comments (complex implementations)

### Best Practices

1. **Make it optional**: Use "N/A" checkbox for irrelevant items
2. **Keep it short**: 6-8 items max to avoid checkbox fatigue
3. **Add context**: Brief explanations of when each doc needs updating
4. **Review periodically**: Adjust checklist based on team needs

---

## 3. Documentation Debt Tracking

### When to Use

- **Development pace**: Fast iteration with tight deadlines
- **Problem**: Documentation falling behind implementation
- **Team culture**: Willing to treat docs as first-class technical debt

### What It Solves

Provides a structured way to acknowledge documentation gaps without blocking development, then prioritize fixes.

### Implementation

**Simple Approach** (recommended): lightweight tracking using:
- Inline `TODO:` comments in documentation files
- GitHub Issues with `documentation` label
- Code review enforcement

**Advanced Tracking** (for larger teams): Track documentation debt in PROJECT_PLAN.md or a dedicated tracker

**Priority Levels**:
- **High**: New architecture undocumented, onboarding blockers → Address current sprint
- **Medium**: Missing examples, incomplete guides → Next sprint
- **Low**: Minor inconsistencies, missing diagrams → Backlog

### Best Practices

1. **Don't let high priority accumulate**: If >5 high-priority items, halt new features
2. **Root cause analysis**: If debt builds up consistently, strengthen Definition of Done
3. **Time allocation**: Reserve 10-15% of sprint capacity for documentation
4. **Code review enforcement**: Reviewer asks "Does this need documentation?" in every PR

---

## 4. Conflict Detection Patterns

### When to Use

- **Team size**: 3+ developers editing documentation
- **Problem**: Contradictory information appearing across docs
- **Culture**: Proactive about documentation quality

### What It Solves

Prevents documentation from containing contradictory or inconsistent information that confuses AI agents and developers.

### Severity Levels

Documentation conflicts fall into three categories:

#### 🔴 CRITICAL - Immediate Warning

**Trigger**: Contradictory architectural decisions or setup instructions

**Examples**:
- Root CLAUDE.md says "use PostgreSQL", database/CLAUDE.md says "use MongoDB"
- ROADMAP.md says "Q1: Migrate to microservices", code docs describe monolith patterns
- Setup instructions have different Python version requirements

**Response**: Pause task, alert team immediately, resolve before merging

**Detection**:
- Manual: Check during PR review
- Automated: Search for conflicting keywords (future: validation script)

#### 🟡 MODERATE - Batch at Task End

**Trigger**: Inconsistent design patterns or terminology

**Examples**:
- One CLAUDE.md calls it "repository pattern", another calls it "DAO pattern" (same thing)
- Inconsistent naming conventions across modules
- Different code style examples

**Response**: Collect issues, report at end of task/sprint, prioritize for next sprint

#### 🟢 MINOR - Low Priority Batch

**Trigger**: Wording differences, stylistic inconsistencies

**Examples**:
- Different phrasing for similar concepts
- Inconsistent emoji usage
- Minor formatting differences

**Response**: Add to documentation debt as low priority, fix during dedicated cleanup sprints

### Conflict Report Format

When a conflict is detected, document it:

```markdown
## Documentation Conflict Report

**Detected**: 2025-01-31
**Severity**: 🔴 CRITICAL
**Reporter**: [Team Member]

### Contradiction

**Location 1**: `CLAUDE.md:45`
> "Use Redis for session storage"

**Location 2**: `auth-service/CLAUDE.md:120`
> "Sessions are stored in PostgreSQL for ACID guarantees"

### Impact

- AI agents will receive contradictory context
- New developers unsure which approach to follow
- May lead to inconsistent implementations

### Suggested Fix

**Option A**: Update auth-service/CLAUDE.md to use Redis (aligns with root decision)
**Option B**: Update root CLAUDE.md to reflect PostgreSQL decision (includes rationale)

**Recommendation**: Option B - PostgreSQL decision is more recent and has technical justification

### Resolution

- [ ] Update `CLAUDE.md:45` with PostgreSQL approach
- [ ] Add rationale for PostgreSQL over Redis
- [ ] Update PROJECT_PLAN.md to track this decision
- [ ] Verify no other docs mention Redis sessions
```

### Manual Detection Checklist

Run this checklist before major releases or quarterly:

```markdown
## Documentation Consistency Checklist

- [ ] Root CLAUDE.md architecture matches subfolder CLAUDE.md details
- [ ] ROADMAP.md strategic decisions reflected in implementation docs
- [ ] Technology choices consistent across all CLAUDE.md files
- [ ] Consistent naming for patterns, components, and acronyms
- [ ] Environment variables and version requirements consistent
- [ ] Code examples use current APIs and match project structure
- [ ] All internal links working, no circular contradictions
```

---

## 5. Multi-Folder Strategy Guide

### When to Use

- **Project evolution**: Starting simple, growing complex
- **Question**: "When should I split CLAUDE.md into subfolders?"

### What It Solves

Provides heuristics for deciding when and how to create subfolder CLAUDE.md files.

### Decision Framework

#### Create a Subfolder CLAUDE.md When:

**Threshold 1: Size** (5+ files in a folder)
```
api/
├── routes.py
├── middleware.py
├── validators.py
├── serializers.py
├── errors.py
└── utils.py
```
**Trigger**: If explaining all these files in root CLAUDE.md takes >500 words, consider subfolder CLAUDE.md

**Threshold 2: Complexity** (distinct architectural pattern)
```
data-pipeline/
├── extractors/
├── transformers/
├── loaders/
└── orchestrator.py
```
**Trigger**: If this module has its own design patterns (ETL pattern), deserves subfolder CLAUDE.md

**Threshold 3: Team** (dedicated owner/team)
```
frontend/
└── [Frontend team owns this]
```
**Trigger**: If a team exclusively works in this area, subfolder CLAUDE.md helps autonomy

**Threshold 4: Integration** (external-facing)
```
api-gateway/
└── [Public API endpoints]
```
**Trigger**: If external consumers need documentation, subfolder CLAUDE.md provides focused context

#### Keep in Root CLAUDE.md When:

- **Few files**: <5 files in folder
- **Simple utility**: No distinct architecture (e.g., `utils/`)
- **Rarely changed**: Stable code that doesn't evolve
- **Shared knowledge**: Entire team familiar, no need for dedicated docs

### Migration Strategy

**Starting New Project**:
1. Begin with root CLAUDE.md only
2. Document everything there until it feels unwieldy (>2000 words)
3. Identify natural boundaries (see thresholds above)
4. Split into subfolder CLAUDE.md files

**Splitting an Existing Root CLAUDE.md**:
1. Identify section that meets threshold criteria
2. Create subfolder CLAUDE.md with:
   - Breadcrumbs back to root
   - Architecture specific to that module
   - Design patterns and integration guides
3. Update root CLAUDE.md:
   - Replace detailed section with brief overview (2-3 sentences)
   - Add link to subfolder CLAUDE.md
   - Update task navigation table
4. Update DOCS.md index if you have one

### Example: Before and After Split

**Before** (Root CLAUDE.md getting too long):
```markdown
## ML Workflow Architecture

The ML workflow handles end-to-end machine learning... [500 words]

### Data Pipeline
Data ingestion and preprocessing... [300 words]

### Model Training
Training loops and experiment tracking... [400 words]

[Total: 1200 words just on ML workflow]
```

**After Split**:

**Root CLAUDE.md**:
```markdown
## ML Workflow Architecture

The ML workflow handles end-to-end ML pipeline from data to trained models.

**Architecture**: Raw Data → Preprocessing → Feature Engineering → Training → Evaluation

**See**: `ml-workflow/CLAUDE.md` for detailed architecture, design patterns, and experiment tracking.
```

**ml-workflow/CLAUDE.md**:
```markdown
# ML Workflow Module - Data Science Documentation Example

## 📍 Breadcrumbs
- **New to the project?** → [Root CLAUDE.md](../../CLAUDE.md)

[Full detailed content - 1200 words]
```

### Folder Naming for Documentation

**Good folder names** (clear documentation targets):
- `ml-workflow/` (functional area)
- `feature-engineering/` (specific responsibility)
- `model-training/` (clear architecture)

**Avoid** (too granular for CLAUDE.md):
- `utils/` (catch-all, no specific architecture)
- `helpers/` (vague, likely doesn't need CLAUDE.md)
- `config/` (simple, doesn't need dedicated docs)

---

## 6. Scheduled Retrospectives

### When to Use

- **Team maturity**: Committed to continuous improvement
- **Documentation age**: Framework in use for 2-3+ months
- **Culture**: Blameless retrospectives, data-driven decisions

### What It Solves

Ensures documentation framework evolves with team needs, prevents stagnation or degradation over time.

### Implementation

**Frequency**: Every 2-3 months (quarterly recommended)

**Duration**: 60-90 minutes

**Attendees**: All developers who use the docs + AI agents (Claude, etc.)

### Retrospective Template

#### Part 1: Metrics Review (15 minutes)

**Documentation Health Metrics**:

| Metric | Q1 2025 | Q2 2025 | Trend | Target |
|--------|---------|---------|-------|--------|
| **Time to find info** (avg) | 45s | 30s | ⬇️ Good | <30s |
| **Documentation debt items** | 12 | 8 | ⬇️ Good | <5 high priority |
| **Docs updated in PRs** (%) | 60% | 85% | ⬆️ Good | >80% |
| **Conflicts detected** | 3 critical | 1 critical | ⬇️ Good | 0 critical |
| **AI agent context efficiency** | ? | ? | Track | Qualitative |

**How to Measure**:
- **Time to find info**: Survey team, ask them to time finding specific info
- **Documentation debt**: Count items in PROJECT_PLAN.md debt section
- **Docs updated in PRs**: Manual count or GitHub API
- **Conflicts detected**: Track in conflict reports
- **AI context efficiency**: Ask Claude "Did you find everything you needed in <30s?"

#### Part 2: Qualitative Feedback (20 minutes)

**Discussion Questions**:

1. **Effectiveness**: Did you find what you needed quickly this quarter?
   - What worked well?
   - What was frustrating?

2. **Coverage**: Are the right things documented?
   - What's missing?
   - What's over-documented?

3. **Accuracy**: Is documentation staying up-to-date?
   - What got stale?
   - What's causing drift?

4. **AI Agent Experience**: (Ask Claude to participate!)
   - Were breadcrumbs helpful?
   - Was task navigation effective?
   - Any confusing contradictions?

#### Part 3: Process Review (15 minutes)

**Checklist Review**:
- [ ] Is the PR documentation checklist too long/short?
- [ ] Is documentation debt being addressed promptly?
- [ ] Are subfolder CLAUDE.md files at the right granularity?
- [ ] Is ROADMAP.md strategic enough (not too tactical)?
- [ ] Is PROJECT_PLAN.md updated frequently enough?

**Advanced Features**:
- [ ] Do we need DOCS.md index now? (>10 folders?)
- [ ] Is conflict detection working?
- [ ] Should we automate anything? (validation script, link checker)

#### Part 4: Action Items (20 minutes)

**Template**:

| Issue | Root Cause | Action | Owner | Due |
|-------|------------|--------|-------|-----|
| [e.g., "Can't find auth docs quickly"] | [e.g., "Auth split across 3 files"] | [e.g., "Consolidate in auth/CLAUDE.md"] | [Team Member] | Q3 Sprint 1 |
| [e.g., "ROADMAP.md too detailed"] | [e.g., "Tactical items creeping in"] | [e.g., "Review and move tactical to PROJECT_PLAN"] | [Team Member] | 2025-07-15 |

#### Part 5: Framework Adaptation (10 minutes)

**Questions**:
- Should we add new documentation files? (e.g., SECURITY.md, API.md)
- Should we change the hierarchical guidelines table?
- Should we adopt new advanced features? (see sections 1-5)
- Should we remove/simplify anything?

**Document Decisions**: Update root CLAUDE.md or ADVANCED_FEATURES.md based on outcomes

### Sample Retrospective Outcome

**Date**: 2025-04-15
**Attendees**: [Team members], Claude (AI agent)

**Metrics**:
- Time to find info: 30s avg ✅ (target met)
- Documentation debt: 8 items ⚠️ (target: <5)
- Docs updated in PRs: 85% ✅ (target met)

**Key Findings**:
- ✅ Task navigation in root CLAUDE.md working well
- ⚠️ ML workflow CLAUDE.md needs more examples
- ⚠️ ROADMAP.md has some tactical items that belong in PROJECT_PLAN.md

**Action Items**:
1. [Team Member 1]: Add 3 code examples to ml-workflow/CLAUDE.md by 2025-04-30
2. [Team Member 2]: Review ROADMAP.md, move tactical items to PROJECT_PLAN.md by 2025-04-22
3. Team: Allocate 20% of next sprint to clearing documentation debt

**Framework Changes**:
- Add "Common Code Examples" section template to subfolder CLAUDE.md
- Clarify ROADMAP vs PROJECT_PLAN boundary in root CLAUDE.md

---

## Combining Features

These patterns work best when combined strategically:

### Small Team (2-3 people), Simple Project
- **Start with**: Core framework only (CLAUDE.md, ROADMAP, PROJECT_PLAN, CHANGELOG)
- **Add if needed**: Documentation Debt Tracking (#3)

### Medium Team (4-8 people), Growing Project
- **Core**: All core docs
- **Add**: PR Documentation Checklist (#2), Documentation Debt Tracking (#3)
- **Consider**: Multi-Folder Strategy (#5) as you grow

### Large Team (8+ people), Complex Project
- **Core**: All core docs
- **Add**: All advanced features
- **Automate**: Validation scripts, conflict detection
- **Regular**: Quarterly retrospectives (#6)

---

## Automation Opportunities (Future)

While this framework starts documentation-only, teams may eventually want automation:

### Validation Script Ideas
- Check for broken internal links
- Detect inconsistent terminology (e.g., "repo" vs "repository")
- Find TODO markers in documentation
- Verify all modules with 5+ files have CLAUDE.md

### GitHub Actions Ideas
- Run validation on PR
- Auto-generate DOCS.md index from folder structure
- Check that CHANGELOG.md was updated for feature PRs

### AI-Assisted Ideas
- Use Claude to detect contradictions in docs
- Auto-generate breadcrumb links
- Suggest when to split CLAUDE.md based on file count

**Note**: Start manual, automate only when pain points are clear.

---

**Last Updated**: 2025-01-31
**Status**: Comprehensive guide for advanced patterns

---

**Related Documentation**:
- [README.md](../README.md) - Framework overview
- [CLAUDE.md](../CLAUDE.md) - Core template
- [PROJECT_PLAN.md](../PROJECT_PLAN.md#documentation-debt) - Debt tracking implementation
