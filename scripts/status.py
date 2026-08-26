"""Show the tiny amount of operational state that matters in v0.001."""

from app.database import initialize_database, read_status
from app.settings import Settings


def main() -> None:
    settings = Settings.from_environment()
    initialize_database(settings.db_path)
    status = read_status(settings.db_path)
    asset = status["asset"]
    summary = status["summary"]

    print("CURRENT•SEA v0.001")
    print()
    print("WHERE WE ARE")
    print(f"{asset['development_stage']} — {asset['development_name']}")
    print()
    print("WHAT EXISTS")
    print(f"{asset['name']} ({asset['id']} v{asset['version']})")
    print(f"Economic state: {asset['value_state']}")
    print()
    print("WHAT REALITY HAS DONE")
    print(f"Invocations: {summary['invocation_count']}")
    print(f"Signals returned: {summary['total_signals']}")
    print(f"Average internal duration: {summary['average_duration_ms']:.3f} ms")
    print()
    print("NEXT SMALLEST STEP")
    print("Invoke the asset once with a real sentence and inspect the result.")


if __name__ == "__main__":
    main()

