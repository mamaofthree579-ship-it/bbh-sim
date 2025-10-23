# Contributing to BBH-Sim

Thank you for contributing! Please follow these steps:

1. Fork the repository and create a topic branch.
2. Add tests for new features (unit tests or example runs).
3. Ensure `python -m pytest` passes for new tests.
4. Open a PR with a clear description, linked issue, and reproduction steps.

Parameter-file contributions must include:
- A `params/*.yaml` file with full metadata.
- A short `README` describing intended physics and estimated compute cost.
- Validation logs (constraint residuals, AH data) when possible.

See `ISSUE_TEMPLATE` and `PULL_REQUEST_TEMPLATE` for more details.
