# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
<!-- ## [1.0.0-alpha.2] - Unreleased -->

- Added logging.
- Fixed bug where `UNASSIGNED` nodes were being alerted on as being compromised.
- Refactored `NodeProviderDB`:
  - Implemented connection pooling.
  - Changed database schema.
  - Made class more friendly to database schema changes.
- Fixed an issue where messages longer than 4096 characters could not be sent through Telegram.
- Added a feature to automatically record all node provider info into the database.
- Added a Watchdog script to notify developers as soon as Node Monitor is down.


## [1.0.0-alpha.1] - 2023-10-20

- Fixed `IndexError` bug when a new node is added to the network.
- Fixed `IndexError` bug for nodes with no label info, now displays `N/A`.
- Added feature `node_status_report` to send a once-daily node status report to each user.
- Added the **Slack Bot** to be able to send messages through a slack channel.
- Added a scheduler to dispatch Node Status Reports at a certain time every day.
- Added the **Telegram Bot** to be able to send messages through a telegram chat.
- Deprecated fields from `NodeProviderDB`:
  - `notify_telegram_channel` from the `subscribers` table.
  - `telegram_channel_id` from the `channel_lookup` table.
- Improved `Node Status` / `Node Down` messages to include more information.


## [1.0.0-alpha] - 2023-09-01

- Overhauled the entire codebase.
- Used `mypy` for type checking.
- Used `pytest` for code formatting
- Used `flask` as a webserver to display status information.
- Removed `NodeMonitorDiff` and replaced it with a more simple function, `get_compromised_nodes`.
- Created a `NodeProviderDB` class for storing configuration information for users in a Postgres database.
