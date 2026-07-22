"""Allow ``python -m llm_eval_harness <subcommand>`` (portfolio contract)."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
