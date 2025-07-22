"""
Declarative Operations Framework for Pygetpapers

This module provides a declarative, configuration-driven approach to repository operations
with make-like dependency management for file transformations.
"""

import configparser
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import yaml

from pygetpapers.core.security_framework import (
    ResourceLimitError,
    SecurityError,
    create_security_framework,
)

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations that can be performed."""

    DOWNLOAD = "download"
    CONVERT = "convert"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    EXPORT = "export"
    CLEAN = "clean"


class DependencyType(Enum):
    """Types of dependencies between operations."""

    FILE_EXISTS = "file_exists"
    FILE_ABSENT = "file_absent"
    FILE_NEWER = "file_newer"
    PATTERN_MATCH = "pattern_match"
    CONDITION = "condition"


@dataclass
class Dependency:
    """Represents a dependency between operations."""

    type: DependencyType
    target: str
    condition: Optional[str] = None
    pattern: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Operation:
    """Represents a declarative operation."""

    name: str
    type: OperationType
    description: str
    command: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    timeout: Optional[int] = None
    retries: int = 3


@dataclass
class RepositoryConfig:
    """Configuration for a repository with declarative operations."""

    name: str
    description: str
    base_url: str
    operations: List[Operation] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    file_patterns: Dict[str, str] = field(default_factory=dict)
    transformers: Dict[str, str] = field(default_factory=dict)
    validators: Dict[str, str] = field(default_factory=dict)
    exporters: Dict[str, str] = field(default_factory=dict)


class DeclarativeOperationsManager:
    """
    Manages declarative operations with dependency resolution.

    This class provides a make-like system for managing file transformations
    and operations based on dependencies and conditions.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        base_dir: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the operations manager.

        Args:
            config_path: Path to configuration file
            base_dir: Base directory for safe operations
        """
        self.config_path = config_path
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.repositories: Dict[str, RepositoryConfig] = {}
        self.operations: Dict[str, Operation] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.file_patterns: Dict[str, re.Pattern] = {}

        # Initialize security framework
        self.security = create_security_framework(self.base_dir)

        if config_path:
            self.load_configuration(config_path)

    def load_configuration(self, config_path: str) -> None:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file
        """
        config_path = Path(config_path)

        if config_path.suffix.lower() in [".yaml", ".yml"]:
            self._load_yaml_config(config_path)
        elif config_path.suffix.lower() == ".json":
            self._load_json_config(config_path)
        else:
            self._load_ini_config(config_path)

    def _load_yaml_config(self, config_path: Path) -> None:
        """Load YAML configuration."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            self._parse_config_data(config_data)
        except Exception as e:
            logger.error(f"Error loading YAML config from {config_path}: {e}")
            raise

    def _load_json_config(self, config_path: Path) -> None:
        """Load JSON configuration."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            self._parse_config_data(config_data)
        except Exception as e:
            logger.error(f"Error loading JSON config from {config_path}: {e}")
            raise

    def _load_ini_config(self, config_path: Path) -> None:
        """Load INI configuration."""
        try:
            config = configparser.ConfigParser()
            config.read(config_path, encoding="utf-8")
            self._parse_ini_config(config)
        except Exception as e:
            logger.error(f"Error loading INI config from {config_path}: {e}")
            raise

    def _parse_config_data(self, config_data: Dict[str, Any]) -> None:
        """Parse configuration data from YAML/JSON."""
        # Parse repositories
        for repo_name, repo_data in config_data.get("repositories", {}).items():
            repo_config = self._create_repository_config(repo_name, repo_data)
            self.repositories[repo_name] = repo_config

        # Parse global operations
        for op_name, op_data in config_data.get("operations", {}).items():
            operation = self._create_operation(op_name, op_data)
            self.operations[op_name] = operation

        # Parse file patterns
        for pattern_name, pattern_str in config_data.get("file_patterns", {}).items():
            self.file_patterns[pattern_name] = re.compile(pattern_str)

    def _parse_ini_config(self, config: configparser.ConfigParser) -> None:
        """Parse INI configuration."""
        # Parse repositories
        for section in config.sections():
            if "." not in section and section != "DEFAULT":
                repo_data = dict(config[section])
                repo_config = self._create_repository_config(section, repo_data)
                self.repositories[section] = repo_config

        # Parse operations (sections with dots)
        for section in config.sections():
            if "." in section:
                parts = section.split(".", 1)
                if parts[0] in self.repositories:
                    # Repository-specific operation
                    op_name = f"{parts[0]}_{parts[1]}"
                    op_data = dict(config[section])
                    operation = self._create_operation(op_name, op_data)
                    self.operations[op_name] = operation

    def _create_repository_config(
        self, name: str, data: Dict[str, Any]
    ) -> RepositoryConfig:
        """Create a repository configuration from data."""
        return RepositoryConfig(
            name=name,
            description=data.get("description", f"{name} repository"),
            base_url=data.get("base_url", ""),
            file_patterns=data.get("file_patterns", {}),
            transformers=data.get("transformers", {}),
            validators=data.get("validators", {}),
            exporters=data.get("exporters", {}),
        )

    def _create_operation(self, name: str, data: Dict[str, Any]) -> Operation:
        """Create an operation from data."""
        return Operation(
            name=name,
            type=OperationType(data.get("type", "download")),
            description=data.get("description", ""),
            command=data.get("command", ""),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            dependencies=[
                self._create_dependency(dep) for dep in data.get("dependencies", [])
            ],
            conditions=data.get("conditions", []),
            config=data.get("config", {}),
            enabled=data.get("enabled", True),
            timeout=data.get("timeout"),
            retries=data.get("retries", 3),
        )

    def _create_dependency(self, data: Union[str, Dict[str, Any]]) -> Dependency:
        """Create a dependency from data."""
        if isinstance(data, str):
            return Dependency(type=DependencyType.FILE_EXISTS, target=data)

        return Dependency(
            type=DependencyType(data.get("type", "file_exists")),
            target=data.get("target", ""),
            condition=data.get("condition"),
            pattern=data.get("pattern"),
            description=data.get("description"),
        )

    def check_dependencies(
        self, operation: Operation, working_dir: Path
    ) -> Tuple[bool, List[str]]:
        """
        Check if all dependencies for an operation are satisfied.

        Args:
            operation: Operation to check dependencies for
            working_dir: Working directory for file operations

        Returns:
            Tuple of (satisfied, missing_dependencies)
        """
        missing = []

        for dep in operation.dependencies:
            if not self._check_dependency(dep, working_dir):
                missing.append(f"{dep.type.value}: {dep.target}")

        return len(missing) == 0, missing

    def _check_dependency(self, dependency: Dependency, working_dir: Path) -> bool:
        """Check if a specific dependency is satisfied."""
        target_path = working_dir / dependency.target

        if dependency.type == DependencyType.FILE_EXISTS:
            return target_path.exists()

        elif dependency.type == DependencyType.FILE_ABSENT:
            return not target_path.exists()

        elif dependency.type == DependencyType.FILE_NEWER:
            if not target_path.exists():
                return False
            # Check if target is newer than some reference file
            if dependency.condition:
                ref_path = working_dir / dependency.condition
                if ref_path.exists():
                    return target_path.stat().st_mtime > ref_path.stat().st_mtime
            return True

        elif dependency.type == DependencyType.PATTERN_MATCH:
            if dependency.pattern:
                pattern = re.compile(dependency.pattern)
                return bool(pattern.search(dependency.target))
            return True

        elif dependency.type == DependencyType.CONDITION:
            if dependency.condition:
                return self._evaluate_condition(dependency.condition, working_dir)
            return True

        return True

    def _evaluate_condition(self, condition: str, working_dir: Path) -> bool:
        """Evaluate a condition string."""
        # Simple condition evaluation - can be extended
        if condition.startswith("file_exists:"):
            file_path = condition.split(":", 1)[1]
            return (working_dir / file_path).exists()

        elif condition.startswith("file_absent:"):
            file_path = condition.split(":", 1)[1]
            return not (working_dir / file_path).exists()

        elif condition.startswith("pattern_match:"):
            pattern_str, target = condition.split(":", 2)[1:]
            pattern = re.compile(pattern_str)
            return bool(pattern.search(target))

        return True

    def get_required_operations(
        self, target_files: List[str], working_dir: Path
    ) -> List[Operation]:
        """
        Get operations required to produce target files.

        Args:
            target_files: List of target file paths
            working_dir: Working directory

        Returns:
            List of operations in dependency order
        """
        required_ops = []
        processed = set()

        for target in target_files:
            ops = self._find_operations_for_target(target)
            for op in ops:
                if op.name not in processed:
                    required_ops.append(op)
                    processed.add(op.name)

        # Sort by dependencies
        return self._topological_sort(required_ops)

    def _find_operations_for_target(self, target: str) -> List[Operation]:
        """Find operations that produce a target file."""
        matching_ops = []

        for op in self.operations.values():
            if target in op.outputs or self._matches_pattern(target, op.outputs):
                matching_ops.append(op)

        return matching_ops

    def _matches_pattern(self, target: str, patterns: List[str]) -> bool:
        """Check if target matches any pattern."""
        for pattern in patterns:
            if "*" in pattern or "?" in pattern:
                # Simple glob pattern matching
                import fnmatch

                if fnmatch.fnmatch(target, pattern):
                    return True
            elif target == pattern:
                return True
        return False

    def _topological_sort(self, operations: List[Operation]) -> List[Operation]:
        """Sort operations by dependencies."""
        # Simple topological sort - can be improved
        result = []
        visited = set()

        def visit(op):
            if op.name in visited:
                return
            visited.add(op.name)

            # Visit dependencies first
            for dep in op.dependencies:
                dep_ops = [o for o in operations if dep.target in o.outputs]
                for dep_op in dep_ops:
                    visit(dep_op)

            result.append(op)

        for op in operations:
            visit(op)

        return result

    def execute_operation(
        self, operation: Operation, working_dir: Path, **kwargs
    ) -> bool:
        """
        Execute an operation.

        Args:
            operation: Operation to execute
            working_dir: Working directory
            **kwargs: Additional parameters

        Returns:
            True if successful, False otherwise
        """
        if not operation.enabled:
            logger.info(f"Operation {operation.name} is disabled, skipping")
            return True

        # Check dependencies
        satisfied, missing = self.check_dependencies(operation, working_dir)
        if not satisfied:
            logger.warning(
                f"Dependencies not satisfied for {operation.name}: {missing}"
            )
            return False

        # Check conditions
        for condition in operation.conditions:
            if not self._evaluate_condition(condition, working_dir):
                logger.info(f"Condition not met for {operation.name}: {condition}")
                return True  # Skip operation, don't fail

        # Execute command
        try:
            logger.info(f"Executing operation: {operation.name}")

            # Replace placeholders in command
            command = self._expand_command(operation.command, working_dir, **kwargs)

            # Execute command (simplified - would integrate with existing pygetpapers)
            success = self._run_command(command, working_dir, operation.timeout)

            if success:
                logger.info(f"Operation {operation.name} completed successfully")
            else:
                logger.error(f"Operation {operation.name} failed")

            return success

        except Exception as e:
            logger.error(f"Error executing operation {operation.name}: {e}")
            return False

    def _expand_command(self, command: str, working_dir: Path, **kwargs) -> str:
        """Expand placeholders in command string."""
        # Replace common placeholders
        command = command.replace("{working_dir}", str(working_dir))
        command = command.replace("{timestamp}", datetime.now().isoformat())

        # Replace kwargs
        for key, value in kwargs.items():
            command = command.replace(f"{{{key}}}", str(value))

        return command

    def _run_command(
        self, command: str, working_dir: Path, timeout: Optional[int]
    ) -> bool:
        """Run a command using security framework."""
        try:
            # Parse command to extract operation type and parameters
            if command.startswith("pygetpapers"):
                return self._execute_pygetpapers_command(command, working_dir, timeout)
            else:
                logger.warning(f"Unsupported command type: {command}")
                return False

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return False

    def _execute_pygetpapers_command(
        self, command: str, working_dir: Path, timeout: Optional[int]
    ) -> bool:
        """Execute pygetpapers command using internal APIs."""
        try:
            # Parse command to extract parameters
            parts = command.split()
            if len(parts) < 2:
                logger.error("Invalid pygetpapers command format")
                return False

            # Extract basic parameters
            repository = parts[1] if len(parts) > 1 else None
            query = None
            limit = 100
            output_dir = str(working_dir)
            xml = False
            makecsv = False
            makehtml = False

            # Parse additional parameters
            i = 2
            while i < len(parts):
                if parts[i] == "-q" and i + 1 < len(parts):
                    query = parts[i + 1]
                    i += 2
                elif parts[i] == "--limit" and i + 1 < len(parts):
                    limit = int(parts[i + 1])
                    i += 2
                elif parts[i] == "-o" and i + 1 < len(parts):
                    output_dir = parts[i + 1]
                    i += 2
                elif parts[i] == "-x":
                    xml = True
                    i += 1
                elif parts[i] == "--makecsv":
                    makecsv = True
                    i += 1
                elif parts[i] == "--makehtml":
                    makehtml = True
                    i += 1
                else:
                    i += 1

            # Validate repository is allowed
            if repository and repository not in self.repositories:
                logger.warning(f"Repository not configured: {repository}")
                return False

            # Execute using internal pygetpapers APIs
            return self._execute_repository_operation(
                repository, query, limit, output_dir, xml, makecsv, makehtml
            )

        except Exception as e:
            logger.error(f"Pygetpapers command execution error: {e}")
            return False

    def _execute_repository_operation(
        self,
        repository: str,
        query: str,
        limit: int,
        output_dir: str,
        xml: bool,
        makecsv: bool,
        makehtml: bool,
    ) -> bool:
        """Execute repository operation using internal APIs."""
        try:
            # Import pygetpapers main class
            from pygetpapers.pygetpapers import Pygetpapers

            # Create pygetpapers instance
            pygetpapers = Pygetpapers()

            # Build query namespace (similar to argparse namespace)
            query_namespace = {
                "api": repository,
                "query": query,
                "limit": limit,
                "output": output_dir,
                "xml": xml,
                "pdf": False,  # Add missing pdf parameter
                "supp": False,  # Add missing supp parameter
                "zip": False,  # Add missing zip parameter
                "references": False,  # Add missing references parameter
                "citations": False,  # Add missing citations parameter
                "makecsv": makecsv,
                "makehtml": makehtml,
                "fulltext_html": False,  # Add missing fulltext_html parameter
                "synonym": False,  # Add missing synonym parameter
                "startdate": False,  # Add missing startdate parameter
                "enddate": False,  # Add missing enddate parameter
                "terms": False,  # Add missing terms parameter
                "notterms": False,  # Add missing notterms parameter
                "onlyquery": False,  # Add missing onlyquery parameter
                "filter": None,  # Add missing filter parameter for Crossref
                "noexecute": False,
                "update": False,
                "restart": False,
                "version": False,
                "save_query": False,
                "loglevel": "info",
                "logfile": False,
                "convert_html": False,  # Add missing convert_html parameter
                "process_html": False,  # Add missing process_html parameter
                "enhance_html": False,  # Add missing enhance_html parameter
            }

            # Execute the operation
            logger.info(f"Executing {repository} operation with query: {query}")
            pygetpapers.runs_pygetpapers_for_given_args(query_namespace)

            logger.info(f"Successfully executed {repository} operation")
            return True

        except Exception as e:
            logger.error(f"Repository operation failed: {e}")
            return False

    def create_configuration_template(self, repo_name: str) -> str:
        """Create a configuration template for a new repository."""
        template = f"""
# Declarative Operations Configuration for {repo_name}

repositories:
  {repo_name}:
    name: {repo_name}
    description: {repo_name.title()} repository with declarative operations
    base_url: https://example.com/{repo_name}
    
    # File patterns for dependency checking
    file_patterns:
      xml_files: "*.xml"
      html_files: "*.html"
      pdf_files: "*.pdf"
      metadata_files: "*_metadata.json"
    
    # Available transformers
    transformers:
      xml_to_html: "simple_html"
      xml_to_pdf: "pandoc"
      metadata_to_csv: "pandas"
    
    # Available validators
    validators:
      xml_validator: "lxml"
      json_validator: "jsonschema"
    
    # Available exporters
    exporters:
      csv_export: "pandas"
      json_export: "json"
      xml_export: "lxml"

operations:
  # Download operation
  {repo_name}_download:
    type: download
    description: Download papers from {repo_name}
    command: "pygetpapers -q {{query}} -o {{working_dir}} -x"
    inputs: []
    outputs: ["*.xml", "*_metadata.json"]
    dependencies: []
    conditions: []
    enabled: true
    timeout: 300
    retries: 3
  
  # Convert XML to HTML
  {repo_name}_xml_to_html:
    type: convert
    description: Convert XML files to HTML
    command: "pygetpapers convert-xml-to-html {{input_file}} {{output_file}}"
    inputs: ["*.xml"]
    outputs: ["*.xml.html"]
    dependencies:
      - type: file_exists
        target: "*.xml"
        description: "XML files must exist"
    conditions:
      - "file_absent:*.xml.html"
    enabled: true
    timeout: 60
    retries: 2
  
  # Validate metadata
  {repo_name}_validate_metadata:
    type: validate
    description: Validate metadata files
    command: "pygetpapers validate-metadata {{metadata_file}}"
    inputs: ["*_metadata.json"]
    outputs: ["*_validation.json"]
    dependencies:
      - type: file_exists
        target: "*_metadata.json"
    conditions: []
    enabled: true
    timeout: 30
    retries: 1
  
  # Export to CSV
  {repo_name}_export_csv:
    type: export
    description: Export metadata to CSV
    command: "pygetpapers export-csv {{metadata_file}} {{csv_file}}"
    inputs: ["*_metadata.json"]
    outputs: ["metadata.csv"]
    dependencies:
      - type: file_exists
        target: "*_metadata.json"
      - type: file_absent
        target: "metadata.csv"
    conditions: []
    enabled: true
    timeout: 30
    retries: 1

# Global file patterns
file_patterns:
  xml_files: ".*\\.xml$"
  html_files: ".*\\.html$"
  pdf_files: ".*\\.pdf$"
  metadata_files: ".*_metadata\\.json$"
  validation_files: ".*_validation\\.json$"
"""
        return template


# Example usage and integration
def create_declarative_config_for_repository(repo_name: str, config_path: str) -> None:
    """
    Create a declarative configuration file for a repository.

    Args:
        repo_name: Name of the repository
        config_path: Path to save the configuration file
    """
    manager = DeclarativeOperationsManager()
    template = manager.create_configuration_template(repo_name)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(template)

    logger.info(f"Created declarative configuration template at {config_path}")


def example_usage():
    """Example of how to use the declarative operations framework."""

    # Create manager
    manager = DeclarativeOperationsManager("config/declarative_operations.yaml")

    # Define target files
    working_dir = Path(".", "corpus")
    target_files = ["paper1.xml.html", "metadata.csv"]

    # Get required operations
    required_ops = manager.get_required_operations(target_files, working_dir)

    # Execute operations
    for op in required_ops:
        success = manager.execute_operation(op, working_dir, query="cancer")
        if not success:
            logger.error(f"Failed to execute operation: {op.name}")
            break
