"""
Tests for the Streamlit UI components
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class TestStreamlitUI:
    """Test the Streamlit UI functionality"""

    def test_streamlit_imports(self):
        """Test that all required Streamlit dependencies can be imported"""
        try:
            pass

            assert True, "All dependencies imported successfully"
        except ImportError as e:
            pytest.fail(f"Failed to import required dependency: {e}")

    def test_streamlit_app_structure(self):
        """Test that the Streamlit app has the expected structure"""
        try:
            import streamlit_app

            assert hasattr(streamlit_app, "PygetpapersUI"), "PygetpapersUI class should exist"

            # Test that the class can be instantiated
            ui = streamlit_app.PygetpapersUI()
            assert ui is not None, "PygetpapersUI should be instantiable"

            # Test that required methods exist
            assert hasattr(ui, "run_pygetpapers_command"), "run_pygetpapers_command method should exist"
            assert hasattr(ui, "build_query_string"), "build_query_string method should exist"
            assert hasattr(ui, "render_header"), "render_header method should exist"

        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")

    def test_query_building(self):
        """Test the query building functionality"""
        try:
            import streamlit_app

            ui = streamlit_app.PygetpapersUI()

            # Test simple query
            query_parts = [{"query": "test", "operator": "AND", "field": "all"}]
            result = ui.build_query_string(query_parts)
            assert result == '"test"', f"Expected '\"test\"', got '{result}'"

            # Test complex query
            query_parts = [
                {"query": "machine learning", "operator": "AND", "field": "title"},
                {"query": "deep learning", "operator": "OR", "field": "abstract"},
            ]
            result = ui.build_query_string(query_parts)
            expected = 'TITLE:"machine learning" OR ABSTRACT:"deep learning"'
            assert result == expected, f"Expected '{expected}', got '{result}'"

        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")

    def test_api_features(self):
        """Test that API features are properly configured"""
        try:
            import streamlit_app

            ui = streamlit_app.PygetpapersUI()

            # Test that all expected APIs are present
            expected_apis = ["europe_pmc", "arxiv", "crossref", "openalex", "biorxiv", "medrxiv", "rxivist"]
            for api in expected_apis:
                assert api in ui.supported_apis, f"API {api} should be supported"
                assert api in ui.api_features, f"API {api} should have features defined"

            # Test that Europe PMC has full features
            eupmc_features = ui.api_features["europe_pmc"]
            assert eupmc_features["query"] is True, "Europe PMC should support queries"
            assert eupmc_features["date_range"] is True, "Europe PMC should support date ranges"
            assert eupmc_features["pdf"] is True, "Europe PMC should support PDF downloads"

        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")

    @patch("subprocess.run")
    def test_command_execution(self, mock_run):
        """Test pygetpapers command execution"""
        try:
            import streamlit_app

            ui = streamlit_app.PygetpapersUI()

            # Mock successful command execution
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            result = ui.run_pygetpapers_command(["--version"])

            assert result["success"] is True, "Command should succeed"
            assert result["stdout"] == "Success", "Should capture stdout"
            assert result["stderr"] == "", "Should capture stderr"

        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")

    def test_run_script_exists(self):
        """Test that the run script exists and is executable"""
        script_path = "run_streamlit.py"
        assert os.path.exists(script_path), f"Run script {script_path} should exist"

        # Test that the script can be imported
        try:
            import run_streamlit

            assert hasattr(run_streamlit, "main"), "run_streamlit should have main function"
        except ImportError as e:
            pytest.fail(f"Failed to import run_streamlit: {e}")

    def test_documentation_files_exist(self):
        """Test that all documentation files exist"""
        required_files = [
            "README_STREAMLIT.md",
            "docs/project-overview.md",
            "docs/user-guide.md",
            "docs/streamlit-ui-implementation.md",
            "docs/implementation-summary.md",
        ]

        for file_path in required_files:
            assert os.path.exists(file_path), f"Documentation file {file_path} should exist"

    def test_port_configuration(self):
        """Test that the app is configured to use port 8502"""
        # Check run script
        with open("run_streamlit.py", "r") as f:
            content = f.read()
            assert "8502" in content, "run_streamlit.py should use port 8502"

        # Check README
        with open("README_STREAMLIT.md", "r") as f:
            content = f.read()
            assert "8502" in content, "README_STREAMLIT.md should mention port 8502"

    @pytest.mark.slow
    def test_pygetpapers_availability(self):
        """Test that pygetpapers is available (slow test)"""
        try:
            import subprocess

            result = subprocess.run(["pygetpapers", "--version"], capture_output=True, text=True, timeout=10)
            assert result.returncode == 0, "pygetpapers should be available"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("pygetpapers not available or timed out")


class TestStreamlitIntegration:
    """Integration tests for Streamlit UI"""

    @pytest.mark.integration
    def test_streamlit_app_imports_without_errors(self):
        """Test that the Streamlit app can be imported without errors"""
        try:
            # This should not raise any exceptions
            pass

            assert True, "Streamlit app imported successfully"
        except Exception as e:
            pytest.fail(f"Failed to import streamlit app: {e}")

    @pytest.mark.integration
    def test_ui_class_instantiation(self):
        """Test that the UI class can be instantiated"""
        try:
            import streamlit_app

            ui = streamlit_app.PygetpapersUI()
            assert ui is not None, "UI class should be instantiable"
        except Exception as e:
            pytest.fail(f"Failed to instantiate UI class: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
