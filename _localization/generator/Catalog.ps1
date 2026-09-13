function Read-Catalog {
    $resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path
    $root = Get-Content -LiteralPath $resolvedInput -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Object -Value $root -Name 'Catalog root'
    return $root
}

function Get-EffectSourcePaths {
    $paths = [System.Collections.Generic.List[string]]::new()
    if ([string]::IsNullOrWhiteSpace($SourceListPath)) {
        throw 'SourceListPath with evaluated MSBuild ClCompile/ClInclude items is required for an effect catalog.'
    }
    $resolvedList = (Resolve-Path -LiteralPath $SourceListPath).Path
    foreach ($line in Get-Content -LiteralPath $resolvedList -Encoding UTF8) {
        if (-not [string]::IsNullOrWhiteSpace($line)) {
            $paths.Add([System.IO.Path]::GetFullPath($line.Trim()))
        }
    }

    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $result = [System.Collections.Generic.List[string]]::new()
    foreach ($path in $paths) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Effect source file does not exist: $path"
        }
        $resolved = (Resolve-Path -LiteralPath $path).Path
        if ($seen.Add($resolved)) {
            $result.Add($resolved)
        }
    }
    if ($result.Count -eq 0) {
        throw 'Effect source inputs must be non-empty.'
    }
    return @($result)
}

function Invoke-AeTextScanner {
    [void](Get-EffectSourcePaths)
    $uv = (Get-Command uv.exe -ErrorAction Stop).Source
    $toolsProject = Join-Path $PSScriptRoot '..\tools'
    & $uv run --locked --no-dev --project $toolsProject aetext scan `
        --source-list $SourceListPath `
        --project-root $ProjectRoot `
        --output $BindingReportPath
    if ($LASTEXITCODE -ne 0) {
        throw "AeText source scan failed with exit code $LASTEXITCODE."
    }

    $report = Get-Content -LiteralPath $BindingReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($report.bindings -isnot [object[]] -or $report.bindings.Count -eq 0) {
        throw 'AeText source scan produced no bindings.'
    }
    return $report
}

function ConvertTo-FlatSourceDerivedTranslations {
    param(
        [Parameter(Mandatory = $true)][object]$Translations,
        [Parameter(Mandatory = $true)][object]$ReviewLayout
    )

    $allowedRoles = @('Param', 'Label', 'Popup', 'Topic', 'About', 'Error')
    $expectedRoles = [System.Collections.Generic.Dictionary[string, string]]::new(
        [System.StringComparer]::Ordinal)
    foreach ($section in @($ReviewLayout.sections)) {
        $role = [string]$section.role
        foreach ($entry in @($section.entries)) {
            $id = [string]$entry.stableId
            $expectedRoles[$id] = $role
        }
    }

    $locales = [ordered]@{}
    foreach ($localeProperty in $Translations.PSObject.Properties) {
        Assert-Object -Value $localeProperty.Value -Name "catalog.translations.$($localeProperty.Name)"
        $flat = [ordered]@{}
        foreach ($roleProperty in $localeProperty.Value.PSObject.Properties) {
            $role = [string]$roleProperty.Name
            if (-not ($allowedRoles -ccontains $role)) {
                throw "Unsupported translation Role section: $role"
            }
            Assert-Object -Value $roleProperty.Value -Name (
                "catalog.translations.$($localeProperty.Name).$role")
            foreach ($translationProperty in $roleProperty.Value.PSObject.Properties) {
                $id = [string]$translationProperty.Name
                if ($flat.Contains($id)) {
                    throw "Translation stable ID appears in multiple Role sections: $id"
                }
                if ($expectedRoles.ContainsKey($id) -and $expectedRoles[$id] -cne $role) {
                    throw "Translation Role mismatch for $id expected=$($expectedRoles[$id]) actual=$role"
                }
                $flat[$id] = $translationProperty.Value
            }
        }
        $locales[$localeProperty.Name] = [pscustomobject]$flat
    }
    return [pscustomobject]$locales
}

function Read-EmbeddedEffectCatalog {
    param([Parameter(Mandatory = $true)][object]$Root)

    Assert-Properties -Value $Root -Allowed @(
        'schemaVersion', 'translations') -Name 'catalog'
    if ($Root.schemaVersion -ne 1) {
        throw 'catalog.schemaVersion must be 1.'
    }

    $translationsProperty = $Root.PSObject.Properties['translations']
    if ($null -eq $translationsProperty) {
        throw 'catalog.translations must be an object.'
    }
    Assert-Object -Value $translationsProperty.Value -Name 'catalog.translations'
    $translations = $translationsProperty.Value

    $report = Invoke-AeTextScanner
    $entries = [System.Collections.Generic.List[object]]::new()
    $macros = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::Ordinal)
    $sourceFiles = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::Ordinal)
    foreach ($binding in @($report.bindings)) {
        $id = [string]$binding.stableId
        $entries.Add([pscustomobject]@{
            id = $id
            source = $id
            role = [string]$binding.role
            disposition = [string]$binding.disposition
        })
        if (-not $macros.ContainsKey($id)) {
            $macros[$id] = [string]$binding.original
            $sourceFiles[$id] = [string]$binding.definition.path
        }
    }
    return [pscustomobject]@{
        Translations = ConvertTo-FlatSourceDerivedTranslations `
            -Translations $translations `
            -ReviewLayout $report.reviewLayout
        BindingModel = [pscustomobject]@{ entries = @($entries) }
        SourceMacros = [pscustomobject]@{ Values = $macros; SourceFiles = $sourceFiles }
    }
}
