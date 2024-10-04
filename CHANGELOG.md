# Changelog

## [0.9.7](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.7) (2024-10-04)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.9.6...0.9.7)

**Release highlights:**

- Type checking will now raise errors when using deprecated attributes

**Breaking change pull requests:**

- Do not expose deprecated attributes to type checkers [\#451](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/451) (@sdb9696)

**Implemented enhancements:**

- Enable keep alive for webrtc stream [\#450](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/450) (@sdb9696)

**Documentation updates:**

- Update README.rst [\#444](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/444) (@jamesflores)

**Project maintenance:**

- Migrate workflows to setup-uv github action [\#449](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/449) (@sdb9696)

## [0.9.6](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.6) (2024-09-26)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.9.5...0.9.6)

**Release highlights:**

- Fix for a critical issue due to the ring authorisation api changing. All previous versions of this library will no longer work.

**Implemented enhancements:**

- Event listener capability enabled by default [\#445](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/445) (@sdb9696)

**Fixed bugs:**

- Send client\_id with oauth fetch tokens request [\#446](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/446) (@sdb9696)

## [0.9.5](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.5) (2024-09-19)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.9.4...0.9.5)

**Release highlights:**

- New CLI commands
- Enhancement to the experimental WebRTC stream feature

**Implemented enhancements:**

- Enable multiple webrtc sessions per device [\#440](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/440) (@sdb9696)
- Add cli command to open door on intercom [\#438](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/438) (@sdb9696)
- Add in-home chime support to CLI [\#427](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/427) (@briangoldstein)

**Fixed bugs:**

- Fix max. volume of Ring Chime device. [\#439](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/439) (@daniel-k)
- Fix cli listen command on windows [\#437](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/437) (@sdb9696)

**Project maintenance:**

- Fix testpypi publish workflow to skip duplicates [\#441](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/441) (@sdb9696)
- Tweak the CI to use variables for project names [\#435](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/435) (@sdb9696)
- Fix publish workflow action [\#434](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/434) (@sdb9696)
- Upgrade artifact upload/download github actions [\#433](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/433) (@sdb9696)

**Closed issues:**

- pyproject include = \["LICENSE", "CONTRIBUTING.rst"...\] [\#324](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/324)

## [0.9.4](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.4) (2024-09-05)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.9.3...0.9.4)

**Release highlights:**

- Migrate from poetry to uv for package management
- Bugfixes for in-home-chime

**Implemented enhancements:**

- Add WebRTC live streaming session generation [\#348](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/348) (@sdb9696)

**Fixed bugs:**

- Fix in-home chime duration setter [\#428](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/428) (@briangoldstein)

**Documentation updates:**

- Fix broken links in readme [\#426](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/426) (@briangoldstein)

**Project maintenance:**

- Migrate to uv and add testpypi publishing [\#430](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/430) (@sdb9696)

## [0.9.3](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.3) (2024-09-02)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.9.2...0.9.3)

**Release highlights:**

- The python-ring-doorbell code repository has moved to https://github.com/python-ring-doorbell/python-ring-doorbell
- Fix for enabling in-home chimes - Many thanks @briangoldstein!

**Fixed bugs:**

- Fix active listen alert counter [\#423](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/423) (@sdb9696)
- Fix method to enable in-home doorbell chime [\#419](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/419) (@briangoldstein)

**Documentation updates:**

- Update supported python version in readme [\#422](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/422) (@sdb9696)

**Project maintenance:**

- Migrate repo to python-ring-doorbell github organisation [\#421](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/421) (@sdb9696)
- Remove anyio from dependencies [\#420](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/420) (@dotlambda)

## [0.9.2](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.2) (2024-08-29)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.9.1...0.9.2)

**Release highlights:**

- Fixes the broken event listener by migrating to the new `firebase-messaging` library to support FCM HTTP v1 api
- **breaking** - the `RingEventListener` will only support async queries. Hence `start` and `stop` are now async defs

**Fixed bugs:**

- Fix event listener [\#416](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/416) (@sdb9696)

## [0.9.1](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.1) (2024-08-23)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.9.0...0.9.1)

Hotfix for missing typing_extensions dependency

**Fixed bugs:**

- Fix missing typing\_extensions dependency [\#413](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/413) (@sdb9696)

**Project maintenance:**

- Update contributing docs to remove tox step [\#411](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/411) (@sdb9696)
- Update and add code checkers [\#410](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/410) (@sdb9696)

## [0.9.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.9.0) (2024-08-21)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.12...0.9.0)

**Release highlights:**

- Async support for the library
- Removed python 3.8 support

**Breaking changes:**

- Synchronous api calls are now deprecated.  For example calling `Ring.update_data()` will emit a deprecation warning to use `await Ring.async_update_data()` which should be run within an event loop via `asyncio.run()`.  See `test.py` for an example.
- Calling the deprecated sync api methods from inside a running event loop is not supported.  This is unlikely to affect many consumers as the norm if running in an event loop is to make synchronous api calls from an executor thread.
- Python 3.8 is no longer officially supported and could break in future releases.

**Breaking change pull requests:**

- Drop python3.8 support and enable python3.13 in the CI [\#398](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/398) (@sdb9696)

**Implemented enhancements:**

- Make library fully async [\#361](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/361) (@sdb9696)

**Fixed bugs:**

- Small change to modify the timestamp [\#378](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/378) (@AndrewMohawk)

**Project maintenance:**

- Update instructions for releasing and migrate changelog [\#407](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/407) (@sdb9696)
- Add .vscode folder to gitignore [\#397](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/397) (@sdb9696)
- Update dependencies [\#396](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/396) (@sdb9696)
- Reduce lock and stale workflow frequency [\#388](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/388) (@sdb9696)

## [0.8.12](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.12) (2024-06-27)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.11...0.8.12)

**Merged pull requests:**

- Fix license value in pyproject.toml for better compliance with accepted values [\#386](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/386) (@joostlek)
- Fix stale workflow exclude list [\#377](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/377) (@sdb9696)
- Fix lock and stale workflows [\#376](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/376) (@sdb9696)
- Add stale and lock github workflows [\#375](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/375) (@sdb9696)
- Update dependencies in lock file and pre-commit [\#374](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/374) (@sdb9696)
- Enable windows, macos and pypy in the CI [\#373](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/373) (@sdb9696)
- Update CI to cache pipx poetry app install [\#372](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/372) (@sdb9696)

## [0.8.11](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.11) (2024-04-09)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.10...0.8.11)

**Merged pull requests:**

- Fix get\_device missing authorized doorbots [\#368](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/368) (@sdb9696)

## [0.8.10](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.10) (2024-04-04)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.9...0.8.10)

**Release highlights:**

- py.typed added to library for type checkers

**Merged pull requests:**

- Update RingDevices class for better typing support and add py.typed [\#366](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/366) (@sdb9696)
- Enable more ruff rules [\#365](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/365) (@joostlek)
- Bump ruff to 0.3.5 [\#364](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/364) (@joostlek)

## [0.8.9](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.9) (2024-04-02)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.8...0.8.9)

**Merged pull requests:**

- Fix issue with third party devices returned in the group other [\#362](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/362) (@sdb9696)
- Save gcm credentials in the cli as default [\#360](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/360) (@sdb9696)
- Add typing and mypy checking [\#359](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/359) (@sdb9696)
- Fix readme example and add to test.py [\#358](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/358) (@sdb9696)
- Update CI to use environment caches [\#355](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/355) (@sdb9696)

## [0.8.8](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.8) (2024-03-18)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.7...0.8.8)

**Merged pull requests:**

- Bump cryptography from 41.0.6 to 42.0.0 [\#343](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/343) (@dependabot[bot])
- Handle Intercom unlock event [\#341](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/341) (@sdb9696)
- Add history to Ring Intercom [\#340](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/340) (@cosimomeli)

## [0.8.7](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.7) (2024-02-06)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.6...0.8.7)

**Release highlights:**

- Support for Ring Intercoms. Many thanks to @rautsch & @andrew-rinato for initial PRs and special thanks to @cosimomeli for getting this over the line!

**Merged pull requests:**

- Add history to has\_capability check [\#342](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/342) (@sdb9696)
- Upgrade CI poetry version to 1.7.1 [\#338](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/338) (@sdb9696)
- Fix changelog link [\#337](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/337) (@sdb9696)
- Migrate to ruff [\#336](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/336) (@sdb9696)
- Make changelog autogenerated as part of CI [\#335](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/335) (@sdb9696)
- Fix coverage over-reporting by uploading xml report [\#333](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/333) (@sdb9696)
- Use coveralls github action [\#332](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/332) (@sdb9696)
- Updated Intercom Support \(2024\) [\#330](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/330) (@cosimomeli)
- Bump jinja2 from 3.1.2 to 3.1.3 [\#327](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/327) (@dependabot[bot])
- Remove exec permissions of ring\_doorbell/cli.py [\#323](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/323) (@cpina)
- Bump cryptography from 41.0.5 to 41.0.6 [\#313](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/313) (@dependabot[bot])

## [0.8.6](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.6) (2024-01-25)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.5...0.8.6)

**Breaking change:**

- Breaking change to the listen subpackage api to allow the listener be configurable.

**Merged pull requests:**

- Allow ring listener to be configurable [\#329](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/329) (@sdb9696)
- Thank note for Debian package [\#326](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/326) (@tchellomello)

## [0.8.5](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.5) (2023-12-21)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.4...0.8.5)

**Merged pull requests:**

- Fix history timeformat and bump to 0.8.5 [\#320](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/320) (@sdb9696)

## [0.8.4](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.4) (2023-12-12)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.3...0.8.4)

**Merged pull requests:**

- Add Spotlight Cam Pro and enable motion detection for Stickup Cam [\#316](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/316) (@sdb9696)

## [0.8.3](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.3) (2023-11-27)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.2...0.8.3)

**Merged pull requests:**

- Fix auth when token invalid & rename device\_id parameters [\#311](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/311) (@sdb9696)
- fix typo in the documentation [\#284](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/284) (@ghost)

## [0.8.2](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.2) (2023-11-24)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.1...0.8.2)

**Merged pull requests:**

- Add ring devices and bump version to 0.8.2 [\#310](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/310) (@sdb9696)

## [0.8.1](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.1) (2023-11-15)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.8.0...0.8.1)

**Merged pull requests:**

- Update CI for python 3.12 [\#307](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/307) (@sdb9696)
- Wrap more exceptions in RingError [\#306](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/306) (@sdb9696)

## [0.8.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.8.0) (2023-11-08)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.7...0.8.0)

**Merged pull requests:**

- Add custom exceptions and encapsulate oauth error handling [\#304](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/304) (@sdb9696)

## [0.7.7](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.7) (2023-10-31)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.6...0.7.7)

**Merged pull requests:**

- Improve stability and capabilities of realtime event listener [\#300](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/300) (@sdb9696)

## [0.7.6](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.6) (2023-10-25)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.5...0.7.6)

**Merged pull requests:**

- Fix anyio dependency preventing ha install [\#298](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/298) (@sdb9696)

## [0.7.5](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.5) (2023-10-25)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.4...0.7.5)

**Merged pull requests:**

- Add event listener for getting realtime dings [\#296](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/296) (@sdb9696)
- Add cli commands: devices, groups, dings and history [\#293](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/293) (@sdb9696)
- Add motion detection cli command and improve formatting of show command [\#292](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/292) (@sdb9696)
- Add tests for cli and fix issues with videos [\#290](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/290) (@sdb9696)

## [0.7.4](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.4) (2023-09-27)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.3...0.7.4)

**Merged pull requests:**

- Fix and update cli [\#288](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/288) (@sdb9696)
- Update to pyproject.toml, poetry, and update docs to use yaml config [\#287](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/287) (@sdb9696)

## [0.7.3](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.3) (2023-09-11)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.2...0.7.3)

**Merged pull requests:**

- 0.7.3 release [\#285](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/285) (@sdb9696)
- Add motion detection enabled switch [\#282](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/282) (@sdb9696)
- Fix ci to use up to date python versions and include pre-commit-config [\#281](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/281) (@sdb9696)
- Add support for Floodlight Cam Pro [\#280](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/280) (@twasilczyk)

## [0.7.2](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.2) (2021-12-18)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.1...0.7.2)

**Merged pull requests:**

- Recognize cocoa\_floodlight as a floodlight kind [\#255](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/255) (@mwren)

## [0.7.1](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.1) (2021-08-26)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.7.0...0.7.1)

**Merged pull requests:**

- fix memory growth when calling url\_recording [\#253](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/253) (@prwood80)
- \[dist\] Fix coveralls build issue [\#238](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/238) (@decompil3d)
- \[dist\] Disable Travis now that GH Actions is setup [\#236](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/236) (@decompil3d)
- get\_snapshot\(\) logic to be compliant with legacy [\#234](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/234) (@tchellomello)
- \[dist\] Use GitHub Actions [\#233](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/233) (@decompil3d)
- \[feat\] Add support for Light Groups [\#231](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/231) (@decompil3d)
- fix: prevent multiple device entries for "Python" in the Ring app when using this library [\#228](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/228) (@riptidewave93)
- Fix live streaming json [\#225](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/225) (@JoeDaddy7105)
- Fix Build Errors [\#224](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/224) (@JoeDaddy7105)
- Fixed RingDoorBell.get\_snapshot\(\) and added download [\#218](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/218) (@NSEvent)
- Fix get snapshot based on comments [\#196](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/196) (@dshokouhi)
- Return None if no battery installed [\#185](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/185) (@balloob)

## [0.7.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.7.0) (2021-02-05)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.6.2...0.7.0)

## [0.6.2](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.6.2) (2020-11-21)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.6.1...0.6.2)

## [0.6.1](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.6.1) (2020-09-28)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.6.0...0.6.1)

**Merged pull requests:**

- Add latest device kinds [\#207](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/207) (@jsetton)
- Pushes new documentation to \(http://python-ring-doorbell.readthedocs.io/\) [\#194](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/194) (@tchellomello)
- Drop python 2.7/3.5. Updated readme and test.py examples [\#192](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/192) (@steve-gombos)

## [0.6.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.6.0) (2020-01-14)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.5.0...0.6.0)

**Major breaking change:**

Ring APIs offer 1 endpoint with all device info. 1 with all health for doorbells etc. The API used to make a request from each device to the "all device" endpoint and fetch its own data.

With the new approach we now just fetch the data once and each device will fetch that data. This significantly reduces the number of requests.

See updated [test.py](https://github.com/tchellomello/python-ring-doorbell/blob/0.6.0/test.py) on usage.

Changes:
 - Pass a user agent to the auth class to identify your project (at request from Ring)
 - For most updates, just call `ring.update_all()`. If you want health data (wifi stuff), call `device.update_health_data()` on each device
 - Renamed `device.id` -> `device.device_id`, `device.account_id` -> `device.id` to follow API naming.
 - Call `ring.update_all()` at least once before querying for devices
 - Querying devices now is a function `ring.devices()` instead of property `ring.devices`
 - Removed `ring.chimes`, `ring.doorbells`, `ring.stickup_cams`
 - Cleaned up tests with pytest fixtures
 - Run Black on code to silence hound.



**Merged pull requests:**

- Refactor data handling [\#184](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/184) (@balloob)

## [0.5.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.5.0) (2020-01-12)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.4.0...0.5.0)

**Breaking Change:**

The `Auth` class no longer takes an `otp_callback` but now takes an `otp_code`. It raises `MissingTokenError` if `otp_code` is required. See the [updated example](https://github.com/tchellomello/python-ring-doorbell/blob/261eaf96875e51fc266a5dbfc6198f8cbb8006e0/test.py).

**Implemented enhancements:**

- Removed otp\_callback [\#180](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/180) (@steve-gombos)

**Merged pull requests:**

- Increased timeout from 5 to 10 seconds [\#179](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/179) (@cyberjunky)

## [0.4.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.4.0) (2020-01-11)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.9...0.4.0)

**Major breaking change:**

This release is a major breaking change to clean up the auth and follow proper OAuth2. Big thanks to @steve-gombos for this.

All authentication is now done inside `Auth`. The first time you need username, password and optionally an 2-factor auth callback function. After that you have a token and that can be used.

The old cache file is no longer in use and can be removed.

Example usage in `test.py`.

**Implemented enhancements:**

- Auth and ring class refactor [\#175](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/175) (@steve-gombos)
- Implemented timeouts for HTTP requests methods [\#165](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/165) (@tchellomello)
- Support for device model name property and has capability method [\#116](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/116) (@jsetton)

**Merged pull requests:**

- Blocked user agent temp fix [\#176](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/176) (@steve-gombos)
- Fixed logic and simplified module imports [\#168](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/168) (@tchellomello)
- Fixes for tchellomello/python-ring-doorbell\#162 [\#163](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/163) (@ZachBenz)
- Make consistent requirements.txt and setup.py [\#158](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/158) (@tchellomello)
- Fixed requirements.xt [\#155](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/155) (@tchellomello)
- fix R1705: Unnecessary elif after return \(no-else-return\) [\#151](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/151) (@xernaj)
- Fix for Issue \#146 [\#149](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/149) (@ZachBenz)
- Fix/oauth fail due to blocked user agent [\#143](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/143) (@xernaj)
- Add additional device kinds for new products [\#137](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/137) (@jsetton)
- Add a couple of device kinds [\#135](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/135) (@dshokouhi)
- Fixed pylint and test errors [\#115](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/115) (@tchellomello)
- support of externally powered new stickup cam [\#109](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/109) (@steveww)
- Add support for downloading snapshot from doorbell [\#108](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/108) (@MorganBulkeley)
- Support for Spotlight Battery cameras with multiple battery bays [\#106](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/106) (@evanjd)

## [0.2.9](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.9) (2020-01-03)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.8...0.2.9)

**Implemented enhancements:**

- add timeout to requests [\#164](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/164)

**Closed issues:**

- 3000 DNS queries a minute [\#160](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/160)

## [0.2.8](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.8) (2019-12-27)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.6...0.2.8)

## [0.2.6](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.6) (2019-12-27)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.5...0.2.6)

## [0.2.5](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.5) (2019-12-20)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.3...0.2.5)

## [0.2.3](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.3) (2019-03-05)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.2...0.2.3)

**Implemented enhancements:**

- Feature Request: Add a model property to identify the different products [\#112](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/112)

**Closed issues:**

- MSG\_GENERIC\_FAIL [\#114](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/114)

## [0.2.2](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.2) (2018-10-29)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.1...0.2.2)

## [0.2.1](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.1) (2018-06-15)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.2.0...0.2.1)

## [0.2.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.2.0) (2018-05-16)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.9...0.2.0)

**Closed issues:**

- Push Notification Token [\#61](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/61)

**Merged pull requests:**

- only save token to disk if reuse session is true [\#81](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/81) (@andrewkress)

## [0.1.9](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.9) (2017-11-29)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.8...0.1.9)

**Implemented enhancements:**

- Create a generic update\(\) call which updates all devices under top-level Ring object [\#74](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/74)
- Created generic update method for all devices on Ring top-parent object [\#75](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/75) (@tchellomello)

## [0.1.8](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.8) (2017-11-22)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.7...0.1.8)

## [0.1.7](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.7) (2017-11-14)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.6...0.1.7)

**Implemented enhancements:**

- Doorbell history does not return all events [\#63](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/63)
- Allows `older_than` parameter to history\(\) method [\#69](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/69) (@tchellomello)

**Merged pull requests:**

- Update README.rst [\#66](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/66) (@ntalekt)

## [0.1.6](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.6) (2017-10-19)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.5...0.1.6)

**Implemented enhancements:**

- Add support to Stick Up cameras [\#38](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/38)
- Added floodlight lights and siren support [\#58](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/58) (@jsetton)

## [0.1.5](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.5) (2017-10-17)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.4...0.1.5)

**Implemented enhancements:**

- Split source code into different files [\#54](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/54)
- Fix \_\_init\_\_ methods [\#49](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/49)
- How to get RSSI? [\#47](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/47)
- House keeping: split source code into different files [\#55](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/55) (@tchellomello)
- Refactored unittests [\#53](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/53) (@tchellomello)
- Implemented health parameters reporting \(wifi, wifi\_rssi\) [\#50](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/50) (@tchellomello)

**Merged pull requests:**

- add wifi connection status property [\#48](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/48) (@keeth)
- chime: Support playing motion test sound [\#46](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/46) (@vickyg3)
- adds support for stickup & floodlight cams [\#44](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/44) (@jlippold)

## [0.1.4](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.4) (2017-04-30)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/v0.1.3...0.1.4)

**Merged pull requests:**

- 0.1.4 [\#42](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/42) (@tchellomello)

## [v0.1.3](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/v0.1.3) (2017-03-31)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.2...v0.1.3)

## [0.1.2](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.2) (2017-03-20)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.1...0.1.2)

**Implemented enhancements:**

- Feature request: Change Chime ring [\#19](https://github.com/python-ring-doorbell/python-ring-doorbell/issues/19)
- Allows to filter history by event kind: 'motion', 'on\_demand', 'ding' [\#20](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/20) (@tchellomello)

**Merged pull requests:**

- Extended unittest coverage to check\_alerts [\#30](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/30) (@tchellomello)
- Added new example [\#27](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/27) (@tchellomello)
- Update README.rst [\#26](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/26) (@tchellomello)
- Rebasing master from dev [\#25](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/25) (@tchellomello)
- Added basic structure for docs [\#24](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/24) (@tchellomello)
- Unittests [\#22](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/22) (@tchellomello)
- Introduced check\_alerts\(\) method [\#17](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/17) (@tchellomello)

## [0.1.1](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.1) (2017-03-09)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.1.0...0.1.1)

**Merged pull requests:**

- v0.1.1 [\#18](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/18) (@tchellomello)

## [0.1.0](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.1.0) (2017-02-25)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.0.4...0.1.0)

**Breaking change:**

The code was refactored to allow to manipulate the objects in a better way.

**Implemented enhancements:**

- Refactored project to make it more Pythonish and transparent [\#14](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/14) (@tchellomello)

## [0.0.4](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.0.4) (2017-02-15)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.0.3...0.0.4)

**Merged pull requests:**

- 0.0.4 [\#12](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/12) (@tchellomello)

## [0.0.3](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.0.3) (2017-02-15)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.0.2...0.0.3)

**Merged pull requests:**

- Fixed metadata setup.py [\#11](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/11) (@tchellomello)
- 0.0.3 [\#10](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/10) (@tchellomello)

## [0.0.2](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.0.2) (2017-02-15)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/0.0.1...0.0.2)

## [0.0.1](https://github.com/python-ring-doorbell/python-ring-doorbell/tree/0.0.1) (2017-02-12)

[Full Changelog](https://github.com/python-ring-doorbell/python-ring-doorbell/compare/1f01b44074cb8d72ca40c83b896ea79768fde885...0.0.1)

**Merged pull requests:**

- Merging from dev [\#5](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/5) (@tchellomello)
- Implemented travis, tox tests [\#4](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/4) (@tchellomello)
- Refactored and updated documentation [\#2](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/2) (@tchellomello)
- Make flake8 happy [\#1](https://github.com/python-ring-doorbell/python-ring-doorbell/pull/1) (@tchellomello)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
