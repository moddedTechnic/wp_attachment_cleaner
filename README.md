# Attachment Cleaner

A tool to automatically remove stale attachments from a WordPress site.

Uses the WordPress API to remove attachments from a site if they match certain criteria.


## Installation

1. Clone this repository.
2. Install dependencies with `poetry install`.


## Usage

1. Rename `_env.py.example` to `_env.py`.
2. Set `BASE_URL` to your WordPress site.
3. Set `USERNAME` to the username of a user which can delete attachments.
4. Generate an [Application Password](https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/#Getting-Credentials).
5. Set `PASSWORD` to this Application Password.
6. Run the tool: `poetry run python3 attachment_cleaner`. This will execute a dry-run.


To have the tool delete attachments (rather than perform a dry-run), set the environment variable `WPAC_MODE` to `dangerous`.


It is recommended to set the tool as a cronjob to run periodically.
This will ensure that stale attachments are regularly cleared from the site.

