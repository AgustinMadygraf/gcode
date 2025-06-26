# Idiom and Naming Consistency Checklist

This checklist helps ensure that all new code and documentation contributions follow the project's conventions for language and naming.

## Language Consistency
- [ ] All documentation is written in English (unless otherwise specified by the team).
- [ ] All code comments and docstrings are in English.
- [ ] Domain concepts use the same terms in code and documentation.

## Naming Consistency
- [ ] Class, method, and variable names reflect domain concepts (ubiquitous language).
- [ ] Avoid unnecessary abbreviations or technical jargon not present in the business domain.
- [ ] File and folder names are in English and match the main concept they represent.
- [ ] Ports (interfaces) are named with the `Port` suffix (e.g., `FilenameServicePort`).
- [ ] Adapters are named with the `Adapter` suffix (e.g., `GCodeGeneratorAdapter`).

## Documentation
- [ ] All new or changed models are documented in `/docs/domain_models.md`.
- [ ] All architectural changes are reflected in `/docs/architecture.md`.
- [ ] All changes are logged in `/docs/CHANGELOG.md`.

## Review Process
- [ ] Reviewer checks for language and naming consistency before approving PRs.
- [ ] Inconsistencies are flagged and corrected before merge.

---
_Keep this checklist up to date as conventions evolve._
