"""CLI for buildcost."""
import sys, json, argparse
from .core import Buildcost

def main():
    parser = argparse.ArgumentParser(description="BuildCost — Construction Cost Estimator. AI-powered construction cost estimation from blueprints.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Buildcost()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.generate(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"buildcost v0.1.0 — BuildCost — Construction Cost Estimator. AI-powered construction cost estimation from blueprints.")

if __name__ == "__main__":
    main()
