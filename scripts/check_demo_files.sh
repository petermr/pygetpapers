#!/bin/bash
# Script to check and manage demonstration files

echo "🔍 Demonstration File Checker"
echo "=============================="

# Find demonstration directories
DEMO_DIRS=$(find . -type d \( -name "*_research_output" -o -name "*_demo_output" -o -name "demo_*" -o -name "temp" -o -name "output" \) -not -path "./.git/*" -not -path "./venv*/*" 2>/dev/null)

if [ -z "$DEMO_DIRS" ]; then
    echo "✅ No demonstration directories found"
    exit 0
fi

echo "📁 Found demonstration directories:"
echo ""

TOTAL_SIZE=0
LARGE_FILES_FOUND=false

for dir in $DEMO_DIRS; do
    if [ -d "$dir" ]; then
        dir_size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
        
        echo "📂 $dir"
        echo "   Size: $dir_size"
        echo "   Files: $file_count"
        
        # Check for large files
        large_files=$(find "$dir" -type f -size +1M 2>/dev/null)
        if [ -n "$large_files" ]; then
            echo "   ⚠️  Large files (>1MB):"
            echo "$large_files" | while read file; do
                file_size=$(du -h "$file" 2>/dev/null | cut -f1)
                echo "      $file ($file_size)"
            done
            LARGE_FILES_FOUND=true
        else
            echo "   ✅ All files are small (<1MB)"
        fi
        
        # Add to total size
        dir_bytes=$(du -s "$dir" 2>/dev/null | cut -f1)
        TOTAL_SIZE=$((TOTAL_SIZE + dir_bytes))
        
        echo ""
    fi
done

# Convert total size to human readable
if [ $TOTAL_SIZE -gt 0 ]; then
    if [ $TOTAL_SIZE -gt 1048576 ]; then  # > 1MB
        total_size_human=$(echo "scale=1; $TOTAL_SIZE / 1048576" | bc -l)
        echo "📊 Total demonstration files size: ${total_size_human}MB"
    else
        total_size_human=$(echo "scale=1; $TOTAL_SIZE / 1024" | bc -l)
        echo "📊 Total demonstration files size: ${total_size_human}KB"
    fi
fi

echo ""
echo "💡 Guidelines:"
echo "   ✅ Small demonstration files (<1MB each) are encouraged"
echo "   ⚠️  Large files (>1MB) should be documented or excluded"
echo "   ❌ Very large files (>10MB) will be blocked by pre-commit hook"
echo ""
echo "💡 Benefits of small demo files:"
echo "   - Faster repository cloning"
echo "   - Easier git operations"
echo "   - Better documentation examples"
echo "   - No push issues"

if [ "$LARGE_FILES_FOUND" = true ]; then
    echo ""
    echo "⚠️  Consider documenting large files or moving them to external storage"
    exit 1
else
    echo ""
    echo "✅ All demonstration files are appropriately sized!"
    exit 0
fi 