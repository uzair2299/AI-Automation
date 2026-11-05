param (
    [string]$Goals = "clean install"
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Building smiota-common-model" -ForegroundColor Cyan
Write-Host "Command: mvn $Goals" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$arguments = $Goals -split '\s+'
& mvn $arguments

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n[SUCCESS] Built and installed smiota-common-model to local Maven repository!" -ForegroundColor Green

