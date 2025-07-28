# File Size Alerts

## Overview

Pygetpapers now includes a comprehensive file size alert system that warns users when downloads exceed configurable size thresholds. This feature helps users avoid unexpected large downloads that could consume significant disk space and bandwidth.

## Features

### 🚨 Automatic Size Detection
- Monitors all file downloads in real-time
- Alerts when files exceed 100 MB (configurable)
- Works across all repositories and file types

### 📊 Multiple Alert Channels
- **Console Logging**: Detailed warnings in command-line output
- **UI Warnings**: Visual alerts in Streamlit interface
- **Progress Tracking**: Real-time alerts during downloads
- **File Browser**: Size indicators for existing files

### ⚙️ Configurable Settings
- Customizable size thresholds
- Enable/disable alerts globally
- Environment variable support
- Repository-specific configurations

## Configuration

### Default Settings
```python
DEFAULT_CONFIG = {
    "file_size_alert_threshold_mb": 100,      # Alert at 100 MB
    "file_size_warning_threshold_mb": 50,     # Warning at 50 MB
    "enable_file_size_alerts": True,          # Enable alerts
    "show_ui_warnings": True,                 # Show UI warnings
    "log_large_files": True,                  # Log to console
}
```

### Environment Variables
Set these environment variables to customize behavior:

```bash
# Set alert threshold to 50 MB
export PYGETPAPERS_FILE_SIZE_ALERT_THRESHOLD_MB=50

# Set warning threshold to 25 MB
export PYGETPAPERS_FILE_SIZE_WARNING_THRESHOLD_MB=25

# Disable alerts
export PYGETPAPERS_ENABLE_FILE_SIZE_ALERTS=false

# Disable UI warnings
export PYGETPAPERS_SHOW_UI_WARNINGS=false

# Disable console logging
export PYGETPAPERS_LOG_LARGE_FILES=false
```

### Programmatic Configuration
```python
from pygetpapers.core.file_size_config import FileSizeConfig

# Custom configuration
config = FileSizeConfig({
    "file_size_alert_threshold_mb": 200,
    "enable_file_size_alerts": True,
    "show_ui_warnings": True
})
```

## Usage Examples

### Command Line
When downloading files, you'll see alerts like:
```
🚨 LARGE FILE ALERT: supplementary_data.zip is 150.2 MB (exceeds 100 MB threshold)
⚠️  This large file may take significant time to download and consume substantial disk space.
```

### Streamlit UI
- **File Browser**: Large files show 🚨 icon and warning text
- **Progress Display**: Real-time alerts during downloads
- **File Details**: Size warnings when viewing large files

### Repository Downloads
Alerts are automatically triggered for:
- PDF downloads
- Supplementary file downloads
- XML content downloads
- Any file exceeding the threshold

## Implementation Details

### Core Components

#### 1. File Size Configuration (`pygetpapers/core/file_size_config.py`)
- Manages alert thresholds and settings
- Environment variable support
- Global configuration instance

#### 2. File Utils Integration (`pygetpapers/core/file_utils.py`)
- `check_file_size_alert()` function
- `format_file_size()` utility
- Configurable alert messages

#### 3. Download Tools Integration (`pygetpapers/core/download_tools.py`)
- Automatic size checking in `queries_the_url_and_writes_response_to_destination()`
- Supplementary file size monitoring
- Real-time alert generation

#### 4. Streamlit UI Integration (`pygetpapers/streamlit_app.py`)
- File browser size indicators
- Progress tracking alerts
- File detail warnings

### Alert Flow
1. **Download Initiated**: File download starts
2. **Size Check**: Content size calculated
3. **Threshold Comparison**: Size compared to configured threshold
4. **Alert Generation**: Warnings logged and displayed
5. **User Notification**: Multiple channels notify user

## Best Practices

### For Users
- **Monitor Alerts**: Pay attention to size warnings
- **Plan Storage**: Ensure sufficient disk space
- **Check Bandwidth**: Large files may take time to download
- **Review Content**: Verify large files are needed

### For Developers
- **Configure Appropriately**: Set thresholds for your use case
- **Test Alerts**: Verify alert functionality
- **Monitor Performance**: Large files may impact system performance
- **Document Usage**: Inform users about size implications

## Troubleshooting

### Alerts Not Showing
1. Check if alerts are enabled: `PYGETPAPERS_ENABLE_FILE_SIZE_ALERTS=true`
2. Verify threshold settings
3. Check console output for configuration errors

### False Positives
1. Adjust threshold to appropriate level
2. Use environment variables for temporary changes
3. Disable alerts for specific operations if needed

### Performance Issues
1. Large files may slow download progress
2. Monitor system resources during large downloads
3. Consider downloading during off-peak hours

## Future Enhancements

### Planned Features
- **Size Estimation**: Pre-download size estimation
- **Bandwidth Monitoring**: Download speed tracking
- **Storage Management**: Automatic cleanup suggestions
- **Repository-Specific Settings**: Different thresholds per repository

### Integration Opportunities
- **Progress Bars**: Size-aware progress indicators
- **Batch Operations**: Size limits for batch downloads
- **Storage Quotas**: Disk space monitoring
- **Network Optimization**: Bandwidth-aware downloads

## Related Documentation
- [Repository Fields Schema](repository_fields_schema.md)
- [Demonstration Files Guide](demonstration-files-guide.md)
- [Security Framework](security_framework.md)
- [Streamlit UI Guide](streamlit-ui-implementation.md) 