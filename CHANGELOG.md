# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-02-16

### Added
- **`persona onboard` command** - Structured interview to build USER.md (inspired by ResonantOS)
- **ONBOARD_PROMPT.md template** - Full onboarding protocol documentation
- **E2E test suite** - 10 tests covering all CLI commands
- **ResonantOS comparison** in PHILOSOPHY.md - Prior art acknowledgment

### Fixed
- **ES module `__dirname` bug** - memory.ts now uses proper `import.meta.url` resolution

### Changed
- **Semver compliance** - New features now bump minor version properly

## [0.2.9] - 2026-02-16

### Added
- Onboard command (initial version)

## [0.2.8] - 2026-02-16

### Fixed
- vmem orphaned method moved into MemoryVault class

## [0.2.7] - 2026-02-16

### Added
- PHILOSOPHY.md - Cognitive AI vs LLM scaffolding thesis
- Peter Voss analysis and synthesis

## [0.2.6] - 2026-02-15

### Added
- Memory lifecycle commands (extract, consolidate, prune)
- Session watcher script
- Self-improvement engine

## [0.2.0] - 2026-02-14

### Added
- Initial npm release
- CLI with init, status, vmem, memory commands
- Templates for SOUL.md, USER.md, AGENTS.md
- Vector memory vault (Python + ChromaDB)
- Agent profiles (researcher, coder, scanner, analyst)
