# Script to format all Python files in the current directory and subdirectories

# Get all .py files, excluding those in hidden directories
Get-ChildItem -Recurse -File -Include *.py | Where-Object { -not ($_.FullName -match '\\\..') } | ForEach-Object {
    Write-Host "Formatting file: $($_.FullName)" -ForegroundColor Cyan

    # Run isort and black
    isort $_.FullName
    black $_.FullName
}