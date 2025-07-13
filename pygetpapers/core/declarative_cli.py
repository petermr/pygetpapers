"""
Command Line Interface for Declarative Operations

This module provides CLI commands for the declarative operations framework,
integrating with the existing pygetpapers command structure.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# SECURITY: This module is a design/prototype only
# Actual implementation would require explicit permission for command execution
from .declarative_operations import (
    DeclarativeOperationsManager,
    create_declarative_config_for_repository,
)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_config_command(args: argparse.Namespace) -> int:
    """Create a declarative configuration file for a repository."""
    try:
        create_declarative_config_for_repository(args.repository, args.output)
        print(
            f"✅ Created declarative configuration for {args.repository} at {args.output}"
        )
        return 0
    except Exception as e:
        print(f"❌ Error creating configuration: {e}")
        return 1


def list_operations_command(args: argparse.Namespace) -> int:
    """List available operations from configuration."""
    try:
        manager = DeclarativeOperationsManager(args.config)

        print(f"📋 Operations in {args.config}:")
        print("=" * 50)

        for op_name, operation in manager.operations.items():
            status = "✅ Enabled" if operation.enabled else "❌ Disabled"
            print(f"\n🔧 {op_name}")
            print(f"   Type: {operation.type.value}")
            print(f"   Description: {operation.description}")
            print(f"   Status: {status}")
            print(
                f"   Inputs: {', '.join(operation.inputs) if operation.inputs else 'None'}"
            )
            print(
                f"   Outputs: {', '.join(operation.outputs) if operation.outputs else 'None'}"
            )

            if operation.dependencies:
                print(f"   Dependencies:")
                for dep in operation.dependencies:
                    print(f"     - {dep.type.value}: {dep.target}")

        return 0
    except Exception as e:
        print(f"❌ Error listing operations: {e}")
        return 1


def check_dependencies_command(args: argparse.Namespace) -> int:
    """Check dependencies for operations."""
    try:
        manager = DeclarativeOperationsManager(args.config)
        working_dir = Path(args.working_dir)

        print(f"🔍 Checking dependencies in {working_dir}:")
        print("=" * 50)

        all_satisfied = True

        for op_name, operation in manager.operations.items():
            if args.operation and op_name != args.operation:
                continue

            satisfied, missing = manager.check_dependencies(operation, working_dir)
            status = "✅ Satisfied" if satisfied else "❌ Missing"

            print(f"\n🔧 {op_name}: {status}")

            if not satisfied:
                all_satisfied = False
                print(f"   Missing dependencies:")
                for dep in missing:
                    print(f"     - {dep}")

        if all_satisfied:
            print(f"\n🎉 All dependencies are satisfied!")
            return 0
        else:
            print(f"\n⚠️  Some dependencies are missing.")
            return 1

    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return 1


def execute_operation_command(args: argparse.Namespace) -> int:
    """Execute a specific operation."""
    try:
        manager = DeclarativeOperationsManager(args.config, args.working_dir)
        working_dir = Path(args.working_dir)

        if args.operation not in manager.operations:
            print(f"❌ Operation '{args.operation}' not found in configuration")
            return 1

        operation = manager.operations[args.operation]

        print(f"🚀 Executing operation: {args.operation}")
        print(f"   Working directory: {working_dir}")
        print(f"   Description: {operation.description}")

        # Check dependencies first
        satisfied, missing = manager.check_dependencies(operation, working_dir)
        if not satisfied:
            print(f"❌ Dependencies not satisfied:")
            for dep in missing:
                print(f"   - {dep}")
            return 1

        # Execute operation using internal APIs
        success = manager.execute_operation(
            operation, working_dir, query=args.query, limit=args.limit
        )

        if success:
            print(f"✅ Operation '{args.operation}' completed successfully")
            return 0
        else:
            print(f"❌ Operation '{args.operation}' failed")
            return 1

    except Exception as e:
        print(f"❌ Error executing operation: {e}")
        return 1


def build_targets_command(args: argparse.Namespace) -> int:
    """Build target files by executing required operations."""
    try:
        manager = DeclarativeOperationsManager(args.config, args.working_dir)
        working_dir = Path(args.working_dir)

        print(f"🏗️  Building targets: {', '.join(args.targets)}")
        print(f"   Working directory: {working_dir}")
        print("=" * 50)

        # Get required operations
        required_ops = manager.get_required_operations(args.targets, working_dir)

        if not required_ops:
            print("ℹ️  No operations required for the specified targets")
            return 0

        print(f"📋 Required operations ({len(required_ops)}):")
        for i, op in enumerate(required_ops, 1):
            print(f"   {i}. {op.name} ({op.type.value})")

        # Execute operations in dependency order
        print("\n🚀 Executing operations in dependency order:")

        success_count = 0
        for i, operation in enumerate(required_ops, 1):
            print(f"\n   {i}. {operation.name} - {operation.description}")

            success = manager.execute_operation(
                operation, working_dir, query=args.query, limit=args.limit
            )

            if success:
                print(f"      ✅ Completed successfully")
                success_count += 1
            else:
                print(f"      ❌ Failed")
                # Continue with other operations even if one fails

        print(
            f"\n🎉 Build completed: {success_count}/{len(required_ops)} operations successful"
        )
        return 0 if success_count == len(required_ops) else 1

    except Exception as e:
        print(f"❌ Error building targets: {e}")
        return 1


def validate_config_command(args: argparse.Namespace) -> int:
    """Validate configuration file."""
    try:
        manager = DeclarativeOperationsManager(args.config)

        print(f"🔍 Validating configuration: {args.config}")
        print("=" * 50)

        # Check repositories
        print(f"\n📚 Repositories ({len(manager.repositories)}):")
        for repo_name, repo_config in manager.repositories.items():
            print(f"   ✅ {repo_name}: {repo_config.description}")

        # Check operations
        print(f"\n🔧 Operations ({len(manager.operations)}):")
        for op_name, operation in manager.operations.items():
            status = "✅" if operation.enabled else "❌"
            print(f"   {status} {op_name}: {operation.description}")

        # Check file patterns
        print(f"\n📁 File patterns ({len(manager.file_patterns)}):")
        for pattern_name, pattern in manager.file_patterns.items():
            print(f"   ✅ {pattern_name}: {pattern.pattern}")

        print(f"\n🎉 Configuration is valid!")
        return 0

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Declarative Operations for Pygetpapers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create configuration for a new repository
  pygetpapers declarative create-config biorxiv -o biorxiv_config.yaml
  
  # List all operations
  pygetpapers declarative list-ops -c config.yaml
  
  # Check dependencies
  pygetpapers declarative check-deps -c config.yaml -w ./corpus
  
  # Execute specific operation
  pygetpapers declarative execute crossref_download -c config.yaml -w ./corpus -q "cancer"
  
  # Build target files
  pygetpapers declarative build paper1.xml.html metadata.csv -c config.yaml -w ./corpus -q "cancer"
  
  # Validate configuration
  pygetpapers declarative validate -c config.yaml
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create config command
    create_parser = subparsers.add_parser(
        "create-config", help="Create configuration template"
    )
    create_parser.add_argument("repository", help="Repository name")
    create_parser.add_argument(
        "-o", "--output", required=True, help="Output configuration file"
    )
    create_parser.set_defaults(func=create_config_command)

    # List operations command
    list_parser = subparsers.add_parser("list-ops", help="List available operations")
    list_parser.add_argument("-c", "--config", required=True, help="Configuration file")
    list_parser.set_defaults(func=list_operations_command)

    # Check dependencies command
    check_parser = subparsers.add_parser(
        "check-deps", help="Check operation dependencies"
    )
    check_parser.add_argument(
        "-c", "--config", required=True, help="Configuration file"
    )
    check_parser.add_argument(
        "-w", "--working-dir", default=".", help="Working directory"
    )
    check_parser.add_argument("-o", "--operation", help="Specific operation to check")
    check_parser.set_defaults(func=check_dependencies_command)

    # Execute operation command
    execute_parser = subparsers.add_parser("execute", help="Execute specific operation")
    execute_parser.add_argument("operation", help="Operation name")
    execute_parser.add_argument(
        "-c", "--config", required=True, help="Configuration file"
    )
    execute_parser.add_argument(
        "-w", "--working-dir", default=".", help="Working directory"
    )
    execute_parser.add_argument("-q", "--query", help="Search query")
    execute_parser.add_argument("-l", "--limit", type=int, help="Result limit")
    execute_parser.set_defaults(func=execute_operation_command)

    # Build targets command
    build_parser = subparsers.add_parser("build", help="Build target files")
    build_parser.add_argument("targets", nargs="+", help="Target files to build")
    build_parser.add_argument(
        "-c", "--config", required=True, help="Configuration file"
    )
    build_parser.add_argument(
        "-w", "--working-dir", default=".", help="Working directory"
    )
    build_parser.add_argument("-q", "--query", help="Search query")
    build_parser.add_argument("-l", "--limit", type=int, help="Result limit")
    build_parser.set_defaults(func=build_targets_command)

    # Validate config command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate configuration file"
    )
    validate_parser.add_argument(
        "-c", "--config", required=True, help="Configuration file"
    )
    validate_parser.set_defaults(func=validate_config_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Setup logging
    setup_logging()

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
