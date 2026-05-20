---
name: agent-browser-setup
description: Install and set up the browser toolset for Hermes Agent - enables browser automation tools for web interaction
version: 1.0.0
author: Hermes Agent
tags: [hermes, browser, automation, setup, playwright]
---

# Agent Browser Setup Skill

How to install and enable the browser toolset for Hermes Agent, enabling full browser automation capabilities (navigation, clicking, typing, scrolling, screenshots, vision analysis).

## Steps

1. Enable the browser toolset via CLI:
```bash
hermes tools enable browser
```

2. Install Playwright Python dependency:
```bash
pip install playwright
```

3. Install Chromium browser for Playwright:
```bash
python -m playwright install chromium
```

   - Note: The download is ~280MB and may take several minutes depending on network speed
   - Use background execution with longer timeout if needed: `python -m playwright install chromium &`

4. Verify installation: Browser tools are now available:
   - `browser_navigate` - navigate to URLs
   - `browser_click` - click elements
   - `browser_type` - input text
   - `browser_snapshot` - get accessibility tree snapshot
   - `browser_scroll` - scroll page
   - `browser_back` - back navigation
   - `browser_console` - get console logs
   - `browser_get_images` - list images
   - `browser_vision` - screenshot + AI vision analysis

## Known Issues

- **Anti-bot detection**: Many websites (Zhihu, etc.) detect automated browsers and return 403 blocks. This is expected behavior when not using residential proxies.
- **Bot detection warnings**: Playwright may warn "your OS is not officially supported" on newer Ubuntu versions, but fallback builds usually work fine.
- **Large download**: Chromium is ~280MB, use background download if timeouts occur.

## Notes

- Hermes browser tool supports three modes: local Chromium (this method), Browserbase cloud, and Camofox. Local Chromium is the default and free option.
- After enabling, start a new session with `/reset` for changes to take effect in an existing session.
