# Testing Validation Agent

Autonomous agent for comprehensive Docusaurus site testing and validation.

## Purpose

Executes testing workflows autonomously to verify build quality, performance, accessibility, and deployment readiness for Docusaurus documentation sites.

## Capabilities

### Pre-Deployment Testing
- Build verification (`npm run build`)
- Content validation (check for responsive issues)
- Static accessibility checks
- Configuration validation
- Automated reporting

### Post-Deployment Testing
- Site accessibility checks
- Lighthouse performance audits (if CLI available)
- Content verification
- HTTPS validation
- Deployment workflow status

## Quick Usage

### Build Verification
```
"Validate the build before I deploy"
"Check if the site builds without errors"
```

**Agent will:**
- Run `npm run build`
- Check for errors/warnings
- Verify all modules present
- Create testing report

### Full Validation
```
"Run full testing suite on https://assadsharif.github.io/Hackathon_01/"
"Validate deployed site quality"
```

**Agent will:**
- Check site accessibility
- Run Lighthouse audits
- Verify content present
- Check deployment status
- Generate comprehensive report

### Accessibility Audit
```
"Check accessibility of the built site"
"Validate WCAG compliance"
```

**Agent will:**
- Check heading hierarchy
- Verify image alt text
- Check ARIA attributes
- Verify focus management
- Create accessibility report

## Output

Agent creates `testing-results.md` with:
- Overall pass/fail status
- Build verification results
- Performance scores (if Lighthouse available)
- Accessibility findings
- Deployment status
- Actionable recommendations

## Example Report

```markdown
# Testing Results

**Overall Status**: ✅ PASS

## Build Verification
✅ Build completed successfully
✅ All 7 modules present
✅ No errors or warnings

## Performance (Lighthouse)
Mobile: 96/100 ✅
Desktop: 98/100 ✅
Accessibility: 97/100 ✅

## Recommendations
- No critical issues found
- Site ready for production
```

## Safety

**Will Do:**
- ✅ Read files and configurations
- ✅ Run build commands (read-only)
- ✅ Execute Lighthouse audits
- ✅ Create testing reports

**Will NOT Do:**
- ❌ Modify source code
- ❌ Delete files
- ❌ Commit changes (without approval)
- ❌ Install/uninstall packages

## Requirements

**Minimum:**
- Node.js and npm (for builds)
- Bash (for commands)

**Optional:**
- Lighthouse CLI (for performance audits)
- jq (for JSON parsing)
- GitHub CLI (for workflow status)

## Integration

**With Testing Skill:**
- Agent reads `.claude/skills/testing/SKILL.md` for procedures
- Applies skill's success criteria
- Uses skill's troubleshooting guidance

**With Project:**
- Reads `docusaurus.config.ts`
- Reads `.github/workflows/deploy.yml`
- Analyzes `build/` output
- Creates reports in project root

## Version

**Agent Version**: 1.0.0
**Compatible With**:
- Docusaurus 3.x
- Node.js 18.x, 20.x
- Lighthouse CLI 10.x+

---

**Status**: Production Ready
**Last Updated**: 2025-12-24
