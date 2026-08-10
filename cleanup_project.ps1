# Clean generated and environment files for the resume-ai project.
# Run from the project root with PowerShell: .\cleanup_project.ps1

$paths = @(
    "backend\venv",
    "frontend\node_modules",
    "frontend\dist",
    "backend\chroma_db",
    "backend\uploads",
    "backend\users.db",
    "backend\resumes.db",
    "backend\chroma.sqlite3"
)

Get-ChildItem "backend" -Filter "users.db.bak_*" -File -ErrorAction SilentlyContinue | ForEach-Object {
    $paths += $_.FullName
}

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "Removing: $path"
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Project cleanup complete."
