param(
    [ValidateSet('CN', 'JP_ForCN', 'Both')]
    [string]$Mode = 'Both',

    [switch]$ShowMode,

    [switch]$BuildNow,

    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',

    [ValidateSet('x64', 'Win32')]
    [string]$Platform = 'x64',

    [switch]$AutoDiscover = $true,

    [string[]]$Projects
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$i18nModePropsPath = Join-Path $repoRoot 'Directory.Build.i18n.props'

function Set-I18nBuildMode {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('CN', 'JP_ForCN', 'Both')]
        [string]$TargetMode,

        [Parameter(Mandatory = $true)]
        [string]$PropsPath
    )

    $content = @"
<?xml version="1.0" encoding="utf-8"?>
<Project>
  <PropertyGroup>
    <!-- global i18n build mode: CN | JP_ForCN | Both -->
    <FsI18nBuildMode>$TargetMode</FsI18nBuildMode>
  </PropertyGroup>
</Project>
"@
    Set-Content -Path $PropsPath -Value $content -Encoding utf8BOM
}

function Get-I18nProjects {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $vcxprojFiles = Get-ChildItem -Path $Root -Recurse -Filter *.vcxproj -File
    $result = @()
    foreach ($file in $vcxprojFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        # Strict discovery: only projects that explicitly include an _i18n header in vcxproj.
        if ($content -match '<ClInclude\s+Include="[^"]*_i18n[\\/][^"]+\.h"') {
            $relative = Resolve-Path -Relative $file.FullName
            if ($relative.StartsWith('.\')) {
                $relative = $relative.Substring(2)
            }
            $result += $relative
        }
    }
    return $result | Sort-Object -Unique
}

function Resolve-LangsForBuild {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('CN', 'JP_ForCN', 'Both')]
        [string]$TargetMode
    )

    switch ($TargetMode) {
        'CN'       { return @('CN') }
        'JP_ForCN' { return @('JP_ForCN') }
        'Both'     { return @('CN', 'JP_ForCN') }
    }
}

if ($ShowMode) {
    if (-not (Test-Path $i18nModePropsPath)) {
        Write-Host 'Current i18n build mode: JP_ForCN (default, config file not found)'
        return
    }

    [xml]$xml = Get-Content -Path $i18nModePropsPath -Raw
    $currentMode = $xml.Project.PropertyGroup.FsI18nBuildMode
    if ([string]::IsNullOrWhiteSpace($currentMode)) {
        $currentMode = 'JP_ForCN'
    }

    Write-Host "Current i18n build mode: $currentMode"
    return
}

Set-I18nBuildMode -TargetMode $Mode -PropsPath $i18nModePropsPath

Write-Host "Global i18n build mode set to: $Mode"
Write-Host "Updated: $i18nModePropsPath"
Write-Host 'VS right-click Build now follows this mode:'
Write-Host ' - CN: only CN output'
Write-Host ' - JP_ForCN: only JP_ForCN output'
Write-Host ' - Both: outputs CN and JP_ForCN'

if (-not $BuildNow) {
    return
}

if (-not (Get-Command msbuild -ErrorAction SilentlyContinue)) {
    throw 'msbuild not found in PATH. Please open a Developer PowerShell for Visual Studio.'
}

foreach ($project in $Projects) {
    if (-not [string]::IsNullOrWhiteSpace($project)) {
        if (-not (Test-Path $project)) {
            throw "Project not found: $project"
        }
    }
}

$resolvedProjects = @()
if ($Projects -and $Projects.Count -gt 0) {
    $resolvedProjects = $Projects | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
} elseif ($AutoDiscover) {
    $resolvedProjects = Get-I18nProjects -Root $repoRoot
} else {
    throw 'No projects specified. Provide -Projects or use -AutoDiscover.'
}

if (-not $resolvedProjects -or $resolvedProjects.Count -eq 0) {
    throw 'No i18n-enabled vcxproj found. Please check whether _i18n headers are explicitly included in vcxproj.'
}

$langs = Resolve-LangsForBuild -TargetMode $Mode

Write-Host ''
Write-Host "BuildNow       : true"
Write-Host "Mode           : $Mode"
Write-Host "Configuration  : $Configuration"
Write-Host "Platform       : $Platform"
Write-Host "Projects       : $($resolvedProjects -join ', ')"
Write-Host ''

foreach ($lang in $langs) {
    Write-Host "=== Building language: $lang ==="
    foreach ($project in $resolvedProjects) {
        & msbuild $project /m /p:Configuration=$Configuration /p:Platform=$Platform /p:FsI18nLang=$lang
        if ($LASTEXITCODE -ne 0) {
            throw "Build failed: project=$project lang=$lang"
        }
    }
}

$outRoot = Join-Path $repoRoot '_OutAex'
Write-Host ''
Write-Host "Done. Output root: $outRoot"
Write-Host 'Expected folders by mode:'
Write-Host " - CN       : $(Join-Path $outRoot 'CN')"
Write-Host " - JP_ForCN : $(Join-Path $outRoot 'JP_ForCN')"
