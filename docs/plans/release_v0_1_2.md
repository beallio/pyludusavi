# Plan - Release v0.1.2

Release v0.1.2 to fix the log filename issue.

## Problem Definition
The log filename was incorrectly set to `ludusavi.log` instead of `ludusavi_rCURRENT.log`.

## Architecture Overview
- No architectural changes, just a bug fix.

## Core Data Structures
N/A

## Public Interfaces
N/A

## Dependency Requirements
N/A

## Testing Strategy
- Verified with `test_log_show_filename`.
- All 59 tests passed.

## Release Details
- **Version**: v0.1.2
- **Title**: v0.1.2: Correct log filename
- **Description**: This release corrects the filename targeted by `Ludusavi.log_show()` to `ludusavi_rCURRENT.log`.
