# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

<!-- ## [1.0.0-alpha.1] - Unreleased -->

- Fixed `IndexError` bug when a new node is added to the network.
- Fixed `IndexError` bug for nodes with no label info, now displays `N/A`.
- Added feature `node_status_report` to send a once-daily node status report to each user.


## [1.0.0-alpha] - 2023-09-01

- Overhauled the entire codebase.
- Used `mypy` for type checking.
- Used `pytest` for code formatting
- Used `flask` as a webserver to display status information.
- Removed `NodeMonitorDiff` and replaced it with a more simple function, `get_compromised_nodes`.
- Created a `NodeProviderDB` class for storing configuration information for users in a Postgres database.