# Changelog

All notable changes to this project are documented here. Entries before 2.0.0 are taken from the [GitHub releases](https://github.com/Garulf/Windows-Startup/releases).

## [2.0.0](https://github.com/Garulf/Windows-Startup/compare/v1.0.2...v2.0.0) (2026-11-17)


### ⚠ BREAKING CHANGES

* the plugin now needs Flow Launcher's python_v2 runtime (Flow Launcher 1.17.0 or newer) and no longer uses Flox.

### Features

* port the plugin to pyflowlauncher on the python_v2 runtime ([5c65ad8](https://github.com/Garulf/Windows-Startup/commit/5c65ad88a3bdfda5761070c1c62e0be2067b7d6e))


### Bug Fixes

* list approved entries when the Run key is missing ([c9fb031](https://github.com/Garulf/Windows-Startup/commit/c9fb031a7f40dbebeb3a6db2b9f83129c7607968))
* point the plugin website at the renamed repo ([#1](https://github.com/Garulf/Windows-Startup/issues/1)) ([465c433](https://github.com/Garulf/Windows-Startup/commit/465c4339e31490fc4b3b02f114c88e017fb53181))
* show an error instead of failing when a change needs admin rights ([743dece](https://github.com/Garulf/Windows-Startup/commit/743dece083757b8323e27ff99aec87eee177fbc0))
* use the all-users Startup folder under ProgramData ([39fdf47](https://github.com/Garulf/Windows-Startup/commit/39fdf47a62ad45b8b8cac20ffdb5fb40a5e4302f))

## [1.0.2](https://github.com/Garulf/Windows-Startup/releases/tag/v1.0.2) - 2022-01-12

- Update the Flox requirement

## [1.0.1](https://github.com/Garulf/Windows-Startup/releases/tag/v1.0.1) - 2021-11-17

- More descriptive subtitle

## [1.0.0](https://github.com/Garulf/Windows-Startup/releases/tag/v1.0.0) - 2021-11-16

- Open `.lnk` startup items with their default handler
- Find Startup folder items more reliably
