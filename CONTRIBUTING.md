# ●

There are many ways to contribute, from helping others on [Github](https://github.com/KillianLucas/01/issues) or [Discord](https://discord.gg/Hvz9Axh84z), writing documentation, or improving code.

## What should I work on?

Please pick up a task from [issues](https://github.com/KillianLucas/01/issues).

If you encounter a bug or have a feature in mind, [search if an issue already exists](https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-issues-and-pull-requests#search-by-the-title-body-or-comments). If a related issue doesn't exist, please [open a new issue](https://github.com/KillianLucas/01/issues/new/choose).

# Contribution Guidelines

1. Before taking on significant code changes, please discuss your ideas on [Discord](https://discord.gg/Hvz9Axh84z) to ensure they align with our vision. We want to keep the codebase simple and unintimidating for new users.
2. Fork the repository and create a new branch for your work.
3. Follow the [Running Your Local Fork](https://github.com/KillianLucas/01/blob/main/CONTRIBUTING.md#running-your-local-fork) guide below.
4. Make changes with clear code comments explaining your approach. Try to follow existing conventions in the code.
5. Follow the [Code Formatting and Linting](https://github.com/KillianLucas/01/blob/main/CONTRIBUTING.md#code-formatting-and-linting) guide below.
6. Open a PR into `main` linking any related issues. Provide detailed context on your changes.

We will review PRs when possible and work with you to integrate your contribution. Please be patient as reviews take time. Once approved, your code will be merged.

## Running Your Local Fork

Once you've forked the code and created a new branch for your work, you can run the fork by following these steps:

1. CD into the software folder `/software`
2. Install dependencies `poetry install`
3. Run the program `poetry run 01`

## Code Formatting and Linting

Our project uses [`black`](https://black.readthedocs.io/en/stable/index.html) for code formatting and [`isort`](https://pypi.org/project/isort/) for import sorting via a [`pre-commit`](https://pre-commit.com/) hook to ensure consistent code style across contributions. Please adhere to the following guidelines:

1. **Install Pre-commit Hooks**:

   To automatically format your code every time you make a commit, install the pre-commit hooks.

   ```bash
   cd software # Change into `software` directory if not there already.
   poetry add --dev pre-commit # Install pre-commit as a dev dependency
   pre-commit install
   ```

   After installing, the hooks will automatically check and format your code every time you commit.

2. **Manual Formatting**:

   If you choose not to use the pre-commit hooks, you can manually format your code using:

   ```bash
   black .
   isort .
   ```

3. **Bypassing**:

   If you need to bypass this for some reason, you can `git commit` with the `--no-verify` flag.

### Installing New Dependencies

If you wish to install new dependencies into the project, please use `poetry add package-name`.

### Known Issues

For some, `poetry install` might hang on some dependencies. As a first step, try to run the following command in your terminal:

`export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring`

Then run `poetry install` again. If this doesn't work, please join our [Discord community](https://discord.gg/Hvz9Axh84z) for help.

# Licensing

Contributions to 01 are under AGPL.

# Questions?

Join our [Discord community](https://discord.gg/Hvz9Axh84z) and post in the #General channel to connect with contributors. We're happy to guide you through your first open source contribution to this project!

**Thank you for your dedication and understanding as we continue refining our processes. As we explore this extraordinary new technology, we sincerely appreciate your involvement.**
