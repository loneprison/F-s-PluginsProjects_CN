param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$BindingReportPath,
    [Parameter(Mandatory = $true)][string]$FamilyDefinitionPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [switch]$Sync,
    [switch]$Prune
)

$ErrorActionPreference = 'Stop'
if ($Prune -and -not $Sync) {
    throw '-Prune is valid only with an explicit -Sync write.'
}

$toolsProject = Join-Path $PSScriptRoot 'tools'
$uv = (Get-Command uv.exe -ErrorAction Stop).Source
$arguments = @(
    'run', '--locked', '--no-dev', '--project', $toolsProject, 'aetext', 'sync',
    '--catalog', [System.IO.Path]::GetFullPath($InputPath),
    '--family', [System.IO.Path]::GetFullPath($FamilyDefinitionPath),
    '--bindings', [System.IO.Path]::GetFullPath($BindingReportPath),
    '--output', [System.IO.Path]::GetFullPath($OutputPath)
)
if ($Sync) { $arguments += '--write' }
if ($Prune) { $arguments += '--prune' }
& $uv @arguments
if ($LASTEXITCODE -ne 0) {
    throw "AeText sync command failed with exit code $LASTEXITCODE."
}
