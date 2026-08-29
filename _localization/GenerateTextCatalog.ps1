param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $true)]
    [string]$Namespace,

    [Parameter(Mandatory = $true)]
    [ValidateSet('Effect', 'Settings')]
    [string]$Kind,

    [string]$SourceDirectory,

    [string]$SourceListPath,

    [string]$BindingReportPath,

    [string]$ProjectRoot,

    [string]$FamilyDefinitionPath,

    [string]$RuntimeIdentityPath,

    [switch]$PublicationValidation
)

$ErrorActionPreference = 'Stop'
$issues = [System.Collections.Generic.List[string]]::new()
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
$temporaryOutput = "$resolvedOutput.tmp.$PID.$([Guid]::NewGuid().ToString('N'))"
$ProjectRoot = if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    (Split-Path -Parent $PSScriptRoot)
} else {
    [System.IO.Path]::GetFullPath($ProjectRoot)
}
$FamilyDefinitionPath = if ([string]::IsNullOrWhiteSpace($FamilyDefinitionPath)) {
    Join-Path $PSScriptRoot 'families\fs\generation.json'
} else {
    $FamilyDefinitionPath
}
$RuntimeIdentityPath = if ([string]::IsNullOrWhiteSpace($RuntimeIdentityPath)) {
    Join-Path $PSScriptRoot 'families\fs\runtime-identity.json'
} else {
    $RuntimeIdentityPath
}
$BindingReportPath = if ([string]::IsNullOrWhiteSpace($BindingReportPath)) {
    "$resolvedOutput.bindings.json"
} else {
    [System.IO.Path]::GetFullPath($BindingReportPath)
}

. (Join-Path $PSScriptRoot 'generator\Template.ps1')
. (Join-Path $PSScriptRoot 'generator\Validation.ps1')
. (Join-Path $PSScriptRoot 'generator\Encoding.ps1')
. (Join-Path $PSScriptRoot 'generator\Family.ps1')
. (Join-Path $PSScriptRoot 'generator\Catalog.ps1')
. (Join-Path $PSScriptRoot 'generator\CppOutput.ps1')
. (Join-Path $PSScriptRoot 'generator\EffectGenerator.ps1')
. (Join-Path $PSScriptRoot 'generator\SettingsGenerator.ps1')
. (Join-Path $PSScriptRoot 'generator\FileOutput.ps1')

try {
    if ($Namespace -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') {
        throw "Invalid C++ namespace: $Namespace"
    }
    $root = Read-Catalog
    $family = Read-FamilyDefinition
    $runtimeIdentity = Read-RuntimeIdentity
    $generation = if ($Kind -eq 'Effect') {
        $embeddedCatalog = Read-EmbeddedEffectCatalog -Root $root
        $translationRoot = $embeddedCatalog.Translations
        $bindingModel = $embeddedCatalog.BindingModel
        $sourceMacros = $embeddedCatalog.SourceMacros
        Write-EffectHeader `
            -Root $translationRoot `
            -BindingModel $bindingModel `
            -SourceMacros $sourceMacros `
            -Family $family.Definition `
            -TranslationLocales $family.TranslationLocales `
            -RuntimeIdentity $runtimeIdentity `
            -Mode $embeddedCatalog.Mode
    } else {
        Write-SettingsHeader -Root $root -RuntimeIdentity $runtimeIdentity
    }
    if ($PublicationValidation -and $issues.Count -gt 0) {
        throw "Publication validation failed:`n - $($issues -join "`n - ")"
    }

    $headerBytes = Convert-ToUtf8BomBytes -Lines $generation.HeaderLines
    Write-AtomicBytesIfChanged -ResolvedPath $resolvedOutput -TemporaryPath $temporaryOutput -Bytes $headerBytes
    if ($null -ne $generation.ByteReport) {
        $byteReportPath = "$BindingReportPath.bytes.json"
        $byteReportTemporary = "$byteReportPath.tmp.$PID.$([Guid]::NewGuid().ToString('N'))"
        $byteReportJson = ($generation.ByteReport | ConvertTo-Json -Depth 12) + "`n"
        $byteReportBytes = [System.Text.UTF8Encoding]::new($false).GetBytes($byteReportJson)
        Write-AtomicBytesIfChanged `
            -ResolvedPath $byteReportPath `
            -TemporaryPath $byteReportTemporary `
            -Bytes $byteReportBytes
    }
} catch {
    if ([System.IO.File]::Exists($temporaryOutput)) {
        [System.IO.File]::Delete($temporaryOutput)
    }
    if ([System.IO.File]::Exists($resolvedOutput)) {
        [System.IO.File]::Delete($resolvedOutput)
    }
    throw
}
