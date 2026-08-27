"""Show the tiny amount of operational state that matters in v0.003."""

from app.database import build_engine, initialize_database, read_status
from app.settings import Settings


def main() -> None:
    settings = Settings.from_environment()
    engine = build_engine(settings.database_url)
    initialize_database(engine)
    status = read_status(engine)
    asset = status["asset"]
    summary = status["summary"]

    print("CURRENT•SEA v0.003")
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
    print(f"By source: {summary['by_source'] or {}}")
    print(f"Signals returned: {summary['total_signals']}")
    print(f"Average internal duration: {summary['average_duration_ms']:.3f} ms")
    print()
    print("NEXT SMALLEST STEP")
    print("Deploy the MCP endpoint, verify it, then publish its registry manifest.")
    engine.dispose()


if __name__ == "__main__":
    main()
