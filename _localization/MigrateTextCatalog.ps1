param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$SourceListPath,
    [Parameter(Mandatory = $true)][string]$FamilyDefinitionPath,
    [Parameter(Mandatory = $true)][string]$Namespace,
    [Parameter(Mandatory = $true)][string]$ProjectRoot,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [string]$ProspectiveDirectory,
    [string]$EquivalenceReport,
    [switch]$Migrate
)

$ErrorActionPreference = 'Stop'
$toolsProject = Join-Path $PSScriptRoot 'tools'
$uv = (Get-Command uv.exe -ErrorAction Stop).Source
$arguments = @(
    'run', '--locked', '--no-dev', '--project', $toolsProject, 'aetext', 'migrate',
    '--catalog', [System.IO.Path]::GetFullPath($InputPath),
    '--source-list', [System.IO.Path]::GetFullPath($SourceListPath),
    '--family', [System.IO.Path]::GetFullPath($FamilyDefinitionPath),
    '--namespace', $Namespace,
    '--project-root', [System.IO.Path]::GetFullPath($ProjectRoot),
    '--output', [System.IO.Path]::GetFullPath($OutputPath)
)
if (-not [string]::IsNullOrWhiteSpace($ProspectiveDirectory)) {
    $arguments += @(
        '--prospective-directory',
        [System.IO.Path]::GetFullPath($ProspectiveDirectory))
}
if ($Migrate) {
    if ([string]::IsNullOrWhiteSpace($EquivalenceReport)) {
        throw '-Migrate requires an equivalence report produced from the current inputs.'
    }
    $arguments += @(
        '--apply',
        '--equivalence-report',
        [System.IO.Path]::GetFullPath($EquivalenceReport))
}

& $uv @arguments
if ($LASTEXITCODE -ne 0) {
    throw "AeText migration command failed with exit code $LASTEXITCODE."
}
