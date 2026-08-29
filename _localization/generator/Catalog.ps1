function Read-Catalog {
    $resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path
    $root = Get-Content -LiteralPath $resolvedInput -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Object -Value $root -Name 'Catalog root'
    return $root
}

function ConvertFrom-CStringExpression {
    param(
        [Parameter(Mandatory = $true)][string]$Expression,
        [Parameter(Mandatory = $true)][string]$Macro
    )

    $literalPattern = '"(?<body>(?:\\.|[^"\\])*)"'
    $literals = @([regex]::Matches($Expression, $literalPattern))
    if ($literals.Count -eq 0 -or [regex]::Replace($Expression, $literalPattern, '').Trim().Length -ne 0) {
        throw "Source macro must contain only C string literals: $Macro"
    }

    $builder = [System.Text.StringBuilder]::new()
    foreach ($literal in $literals) {
        $body = [string]$literal.Groups['body'].Value
        for ($index = 0; $index -lt $body.Length; $index++) {
            $character = [char]$body[$index]
            if ($character -ne '\') {
                [void]$builder.Append($character)
                continue
            }
            if (++$index -ge $body.Length) {
                throw "Incomplete C escape in source macro: $Macro"
            }

            $escape = [char]$body[$index]
            $decoded = switch ($escape) {
                'n' { "`n" }
                'r' { "`r" }
                't' { "`t" }
                '\' { '\' }
                '"' { '"' }
                default { $null }
            }
            if ($null -eq $decoded) {
                throw "Unsupported C escape in source macro: $Macro escape=\$escape"
            }
            [void]$builder.Append($decoded)
        }
    }
    return $builder.ToString()
}

function ConvertTo-ProjectRelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $root = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\', '/')
    $resolved = [System.IO.Path]::GetFullPath($Path)
    $prefix = $root + [System.IO.Path]::DirectorySeparatorChar
    if ($resolved.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $resolved.Substring($prefix.Length).Replace('\', '/')
    }
    return $resolved.Replace('\', '/')
}

function Get-EffectSourcePaths {
    param([switch]$RequireSourceList)

    $paths = [System.Collections.Generic.List[string]]::new()
    if (-not [string]::IsNullOrWhiteSpace($SourceListPath)) {
        $resolvedList = (Resolve-Path -LiteralPath $SourceListPath).Path
        foreach ($line in Get-Content -LiteralPath $resolvedList -Encoding UTF8) {
            if (-not [string]::IsNullOrWhiteSpace($line)) {
                $paths.Add([System.IO.Path]::GetFullPath($line.Trim()))
            }
        }
    } elseif ($RequireSourceList) {
        throw 'SourceListPath with evaluated MSBuild ClCompile/ClInclude items is required for a source-derived catalog.'
    } elseif (-not [string]::IsNullOrWhiteSpace($SourceDirectory)) {
        $resolvedSourceDirectory = (Resolve-Path -LiteralPath $SourceDirectory).Path
        foreach ($source in @(Get-ChildItem -LiteralPath $resolvedSourceDirectory -File |
            Where-Object { @('.cpp', '.h', '.hpp') -ccontains $_.Extension.ToLowerInvariant() } |
            Sort-Object Name)) {
            $paths.Add($source.FullName)
        }
    } else {
        throw 'SourceListPath or SourceDirectory is required for Effect catalogs.'
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

function Read-SourceMacros {
    param(
        [Parameter(Mandatory = $true)][object]$BindingModel,
        [Parameter(Mandatory = $true)][string[]]$SourcePaths
    )

    $macros = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::Ordinal)
    $sourceFiles = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::Ordinal)
    $requiredMacros = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($entry in @($BindingModel.entries)) {
        [void]$requiredMacros.Add([string]$entry.source)
    }
    $sourcePattern = '(?m)^[ \t]*#[ \t]*define[ \t]+(?<name>[A-Za-z_][A-Za-z0-9_]*)[ \t]+(?<value>(?:"(?:\\.|[^"\\])*"[ \t]*)+)(?://[^\r\n]*)?\r?$'
    foreach ($path in $SourcePaths) {
        $contents = Get-Content -LiteralPath $path -Raw -Encoding UTF8
        foreach ($match in [regex]::Matches($contents, $sourcePattern)) {
            $name = [string]$match.Groups['name'].Value
            if (-not $requiredMacros.Contains($name)) {
                continue
            }
            $value = ConvertFrom-CStringExpression -Expression ([string]$match.Groups['value'].Value) -Macro $name
            if ($macros.ContainsKey($name) -and $macros[$name] -cne $value) {
                throw "Conflicting source macro definitions: $name"
            }
            $macros[$name] = $value
            $sourceFiles[$name] = ConvertTo-ProjectRelativePath -Path $path
        }
    }
    return [pscustomobject]@{
        Values = $macros
        SourceFiles = $sourceFiles
    }
}

function Invoke-AeTextScanner {
    [void](Get-EffectSourcePaths -RequireSourceList)
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
        if (-not ($allowedRoles -ccontains $role)) {
            throw "Unsupported review layout Role: $role"
        }
        foreach ($entry in @($section.entries)) {
            $id = [string]$entry.stableId
            if ($expectedRoles.ContainsKey($id)) {
                throw "Review layout contains duplicate stable ID: $id"
            }
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

    $bindingsProperty = $Root.PSObject.Properties['bindings']
    $sourceDerived = $null -eq $bindingsProperty
    if ($sourceDerived) {
        Assert-Properties -Value $Root -Allowed @(
            'schemaVersion', 'translations', 'workflow') -Name 'catalog'
        if ($Root.schemaVersion -ne 1) {
            throw 'catalog.schemaVersion must be 1.'
        }
    } else {
        Assert-Properties -Value $Root -Allowed @(
            'bindings', 'translations', 'workflow') -Name 'catalog'
        Assert-Object -Value $bindingsProperty.Value -Name 'catalog.bindings'
    }

    $translationsProperty = $Root.PSObject.Properties['translations']
    if ($null -eq $translationsProperty) {
        throw 'catalog.translations must be an object.'
    }
    Assert-Object -Value $translationsProperty.Value -Name 'catalog.translations'
    $translations = $translationsProperty.Value

    if ($sourceDerived) {
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
            Mode = 'SourceDerived'
        }
    }

    $entries = [System.Collections.Generic.List[object]]::new()
    $allowedRoles = @('Param', 'Label', 'Popup', 'Topic', 'About', 'Error')
    foreach ($roleProperty in $Root.bindings.PSObject.Properties) {
        $role = $roleProperty.Name
        if (-not ($allowedRoles -ccontains $role)) {
            throw "Unsupported effect text role: $role"
        }
        Assert-Object -Value $roleProperty.Value -Name "catalog.bindings.$role"
        foreach ($tokenProperty in $roleProperty.Value.PSObject.Properties) {
            $name = "catalog.bindings.$role.$($tokenProperty.Name)"
            if ($tokenProperty.Value -isnot [string] -or $tokenProperty.Value.Length -eq 0) {
                throw "$name must be a non-empty stable ID string."
            }
            $entries.Add([pscustomobject]@{
                id = [string]$tokenProperty.Value
                source = [string]$tokenProperty.Value
                token = $tokenProperty.Name
                role = $role
                disposition = 'translated'
            })
        }
    }
    if ($entries.Count -eq 0) {
        throw 'catalog.bindings must be a non-empty object.'
    }

    $bindingModel = [pscustomobject]@{ entries = @($entries) }
    $sourcePaths = @(Get-EffectSourcePaths)
    return [pscustomobject]@{
        Translations = $translations
        BindingModel = $bindingModel
        SourceMacros = Read-SourceMacros -BindingModel $bindingModel -SourcePaths $sourcePaths
        Mode = 'Legacy'
    }
}
