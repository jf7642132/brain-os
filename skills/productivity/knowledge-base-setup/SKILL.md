---
name: knowledge-base-setup
description: Automated setup of dynamic knowledge management system
category: productivity
tags: [knowledge, organization, notes, tasks]
---

# Knowledge Base Setup Skill

## Overview
Automated setup of a dynamic, evolving knowledge management system for personal and professional use.

## When to Use
- User requests help setting up a knowledge base
- Need to organize notes, tasks, projects, and interests
- Creating a system that can adapt over time

## Setup Steps

### 1. Create Directory Structure
```bash
mkdir -p ~/.hermes/knowledge/{00-inbox,01-work/{projects,meetings,notes,resources},02-personal/{goals,learning,habits,reflections},03-interests/{hobbies,reading,media,collections},04-tasks/{active,backlog,completed},05-connections/{maps,links,references},06-shares/{reports,presentations,articles},99-archive}
```

### 2. Generate Core Templates
Create template files in each module:
- `00-inbox/README.md` - Quick capture instructions
- `01-work/notes/TEMPLATE.md` - Project note template
- `02-personal/goals/TEMPLATE.md` - Goal tracking template
- `04-tasks/active/TEMPLATE.md` - Task management template
- `README.md` - Main index with navigation

### 3. Configure Workflow
- Set up WeChat integration for quick capture
- Enable automatic categorization suggestions
- Configure regular review reminders (weekly/monthly)

## Dynamic Evolution
- Monthly review: assess module usage, merge/split as needed
- Quarterly optimization: update templates based on usage patterns
- Version control: track framework changes in `99-archive/`

## Integration Points
- **Quick Capture**: User sends content via WeChat → auto-classify to `00-inbox`
- **Knowledge Import**: Convert external articles (Zhihu, blogs, docs) to structured notes
- **Chat Log Extraction**: Extract knowledge from WeChat chat logs (bugs, solutions, best practices) → see `references/wechat-chat-log-extraction.md`
- **Task Sync**: Link tasks to projects and goals
- **Share Export**: Generate reports, presentations, articles from organized content

## Example Workflow
1. User sends "记录：今天想到一个项目..." → stored in `00-inbox/`
2. Weekly review: classify inbox items to appropriate modules
3. Project creation: copy project template, populate with details
4. Regular updates: add progress notes, link related knowledge
5. Monthly export: generate reports or shareable content

## Maintenance
- Monitor directory sizes, suggest cleanup if >100MB
- Review template effectiveness quarterly
- Archive completed projects to `99-archive/`
- Update knowledge maps as connections grow