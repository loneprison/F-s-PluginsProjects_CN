$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$catalogRoot = Join-Path $root '_localization\catalog'
$generator = Join-Path $root '_localization\GenerateTextCatalog.ps1'
$pluginMapPath = Join-Path $root 'Directory.Build.PluginMap.props'
$toolsProject = Join-Path $root '_localization\tools'
$scratch = Join-Path ([System.IO.Path]::GetTempPath()) ("FsTextCatalogTests-" + [Guid]::NewGuid().ToString('N'))
$msbuild = 'C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe'

function Get-ProjectName {
    param([Parameter(Mandatory = $true)][string]$Condition)

    if ($Condition -notmatch "^'\$\(MSBuildProjectName\)'=='([^']+)'$") {
        throw "Unsupported PluginMap condition: $Condition"
    }
    return $Matches[1]
}

function Get-CatalogPath {
    param(
        [Parameter(Mandatory = $true)][System.Xml.XmlElement]$Group,
        [Parameter(Mandatory = $true)][string]$ProjectName
    )

    $directory = $catalogRoot
    if ([string]$Group.FsProjectRole -eq 'Production') {
        $directory = Join-Path $directory ([string]$Group.FsAeCategory)
    } elseif ([string]$Group.FsProjectRole -eq 'Support') {
        $directory = Join-Path $directory '_Support'
    } else {
        $directory = Join-Path $directory "($([string]$Group.FsProjectRole))"
    }
    if ([string]$Group.FsOutputIsolation) {
        $directory = Join-Path $directory ([string]$Group.FsOutputIsolation)
    }

    $catalogName = if ($ProjectName -eq 'FsLanguageSettings') { 'Settings' } else { $ProjectName }
    return Join-Path $directory "$catalogName.json"
}

[System.IO.Directory]::CreateDirectory($scratch) | Out-Null
try {
    if (-not (Test-Path -LiteralPath $msbuild -PathType Leaf)) {
        throw 'MSBuild was not found at the validated Visual Studio location.'
    }
    $processPath = $env:Path
    Remove-Item Env:PATH -ErrorAction SilentlyContinue
    [Environment]::SetEnvironmentVariable('Path', $processPath, 'Process')

    & uv.exe run --locked --no-dev --project $toolsProject aetext sync-classification `
        --repository $root
    if ($LASTEXITCODE -ne 0) {
        throw 'Source-derived classification views are stale. Run uv run aetext sync-classification --apply from _localization/tools.'
    }

    $evaluatedProjects = @{}
    $projectFiles = @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.vcxproj' |
        Sort-Object FullName)
    for ($projectIndex = 0; $projectIndex -lt $projectFiles.Count; $projectIndex++) {
        $manifest = Join-Path $scratch ('project-{0:D4}.txt' -f $projectIndex)
        & $msbuild $projectFiles[$projectIndex].FullName `
            /t:WriteAeTextInventoryManifest `
            /p:Configuration=Debug `
            /p:Platform=x64 `
            "/p:AeTextInventoryOutput=$manifest" `
            /nologo `
            /v:quiet
        if ($LASTEXITCODE -ne 0) {
            throw "MSBuild source evaluation failed: $($projectFiles[$projectIndex].FullName)"
        }
        $lines = @([System.IO.File]::ReadAllLines($manifest))
        $projectLine = @($lines | Where-Object { $_.StartsWith('PROJECT|') })
        if ($projectLine.Count -ne 1) {
            throw "Invalid MSBuild inventory manifest: $manifest"
        }
        $fields = $projectLine[0].Substring(8).Split('|')
        if ($fields.Count -ne 7) {
            throw "Invalid project record in MSBuild inventory manifest: $manifest"
        }
        $sourceList = Join-Path $scratch ("$($fields[1]).sources.txt")
        $sources = @($lines | Where-Object {
            $_.StartsWith('COMPILE|') -or $_.StartsWith('INCLUDE|')
        } | ForEach-Object { $_.Substring($_.IndexOf('|') + 1) })
        [System.IO.File]::WriteAllLines(
            $sourceList,
            $sources,
            [System.Text.UTF8Encoding]::new($false))
        $evaluatedProjects[$fields[1]] = [pscustomobject]@{
            CatalogPath = [System.IO.Path]::GetFullPath($fields[2])
            SourceListPath = $sourceList
            FamilyDefinitionPath = [System.IO.Path]::GetFullPath($fields[6])
        }
    }

    [xml]$pluginMap = Get-Content -LiteralPath $pluginMapPath -Raw
    $groups = @($pluginMap.Project.PropertyGroup)
    $expectedCatalogs = [System.Collections.Generic.List[string]]::new()

    foreach ($group in $groups) {
        $projectName = Get-ProjectName -Condition ([string]$group.Condition)
        $catalogPath = Get-CatalogPath -Group $group -ProjectName $projectName
        if (-not [System.IO.File]::Exists($catalogPath)) {
            throw "Missing catalog for project $projectName`: $catalogPath"
        }
        $expectedCatalogs.Add([System.IO.Path]::GetFullPath($catalogPath))
        if (-not $evaluatedProjects.ContainsKey($projectName)) {
            throw "No evaluated project was found for $projectName."
        }
        if ($evaluatedProjects[$projectName].CatalogPath -cne [System.IO.Path]::GetFullPath($catalogPath)) {
            throw "Evaluated catalog path mismatch for $projectName."
        }
        if (-not [System.IO.File]::Exists($evaluatedProjects[$projectName].FamilyDefinitionPath)) {
            throw "Evaluated family definition does not exist for $projectName."
        }

        $isSettings = $projectName -eq 'FsLanguageSettings'
        $kind = if ($isSettings) { 'Settings' } else { 'Effect' }
        $namespace = if ($isSettings) {
            'FsLanguageSettingsText'
        } else {
            ([regex]::Replace($projectName, '[^A-Za-z0-9_]', '_') + 'Text')
        }
        $outputPath = Join-Path $scratch "$namespace.generated.h"
        $arguments = @{
            InputPath = $catalogPath
            OutputPath = $outputPath
            Namespace = $namespace
            Kind = $kind
            FamilyDefinitionPath = $evaluatedProjects[$projectName].FamilyDefinitionPath
            PublicationValidation = $true
        }
        if (-not $isSettings) {
            $arguments.SourceListPath = $evaluatedProjects[$projectName].SourceListPath
            $arguments.BindingReportPath = Join-Path $scratch "$namespace.bindings.json"
            $arguments.ProjectRoot = $root
        }

        & $generator @arguments
        if (-not [System.IO.File]::Exists($outputPath)) {
            throw "Catalog generation failed for project $projectName."
        }

        if ($projectName -eq 'PluginSkeleton') {
            $expectedGeneratedHash = '7878959D5818628CC0691B81708B07975B9DCADDCC0BB0061D064BD75ABF706B'
            $generatedHash = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash
            if ($generatedHash -cne $expectedGeneratedHash) {
                throw "PluginSkeleton generated text changed: expected $expectedGeneratedHash, got $generatedHash."
            }
            $workflowCatalogPath = Join-Path $scratch 'PluginSkeleton.workflow.json'
            $workflowOutputPath = Join-Path $scratch 'PluginSkeleton.workflow.generated.h'
            $workflowBindingPath = Join-Path $scratch 'PluginSkeleton.workflow.bindings.json'
            $workflowCatalog = Get-Content -LiteralPath $catalogPath -Raw -Encoding UTF8 |
                ConvertFrom-Json
            $workflowCatalog | Add-Member -NotePropertyName workflow -NotePropertyValue ([pscustomobject]@{
                zh = [pscustomobject]@{
                    Param = [pscustomobject]@{ L10N_PARAM_COLOR = 'reviewed' }
                }
            })
            $workflowCatalog | ConvertTo-Json -Depth 12 |
                Set-Content -LiteralPath $workflowCatalogPath -Encoding UTF8
            $workflowArguments = @{
                InputPath = $workflowCatalogPath
                OutputPath = $workflowOutputPath
                Namespace = $namespace
                Kind = $kind
                FamilyDefinitionPath = $evaluatedProjects[$projectName].FamilyDefinitionPath
                SourceListPath = $evaluatedProjects[$projectName].SourceListPath
                BindingReportPath = $workflowBindingPath
                ProjectRoot = $root
                PublicationValidation = $true
            }
            & $generator @workflowArguments
            if ((Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash -cne
                (Get-FileHash -LiteralPath $workflowOutputPath -Algorithm SHA256).Hash) {
                throw 'PluginSkeleton workflow metadata changed generated text bytes.'
            }
        }
    }

    $popupFixtureRoot = Join-Path $scratch 'popup-separator-fixture'
    [System.IO.Directory]::CreateDirectory($popupFixtureRoot) | Out-Null
    $popupSource = Join-Path $popupFixtureRoot 'PopupFixture.cpp'
    $popupSourceList = Join-Path $popupFixtureRoot 'sources.txt'
    $popupCatalog = Join-Path $popupFixtureRoot 'PopupFixture.json'
    [System.IO.File]::WriteAllText(
        $popupSource,
        "#define L10N_MENU `"One|(-|Two`"`nauto menu = AETEXT_POPUP(strings, L10N_MENU);`n",
        [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllLines(
        $popupSourceList,
        @($popupSource),
        [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText(
        $popupCatalog,
        (@{
            schemaVersion = 1
            translations = @{
                en = @{ Popup = @{ L10N_MENU = @{ useSource = $true } } }
                zh = @{ Popup = @{ L10N_MENU = 'One|ordinary text|Two' } }
            }
        } | ConvertTo-Json -Depth 8),
        [System.Text.UTF8Encoding]::new($false))
    $popupRejected = $false
    try {
        & $generator `
            -InputPath $popupCatalog `
            -OutputPath (Join-Path $popupFixtureRoot 'PopupFixture.generated.h') `
            -Namespace 'PopupFixtureText' `
            -Kind 'Effect' `
            -FamilyDefinitionPath (Join-Path $root '_localization\families\fs\generation.json') `
            -SourceListPath $popupSourceList `
            -BindingReportPath (Join-Path $popupFixtureRoot 'bindings.json') `
            -ProjectRoot $popupFixtureRoot `
            -PublicationValidation $true
    } catch {
        if ([string]$_ -notlike '*Popup separator structure mismatch*') {
            throw
        }
        $popupRejected = $true
    }
    if (-not $popupRejected) {
        throw 'Popup separator position mismatch was not rejected by the generator.'
    }

    $actualCatalogs = @(Get-ChildItem -LiteralPath $catalogRoot -Recurse -File -Filter '*.json' |
        ForEach-Object { $_.FullName })
    $difference = @(Compare-Object -ReferenceObject @($expectedCatalogs) -DifferenceObject $actualCatalogs -CaseSensitive)
    if ($difference.Count -ne 0) {
        throw "Catalog files do not match Directory.Build.PluginMap.props:`n$($difference | Out-String)"
    }

    Write-Host "Validated $($groups.Count) localization catalogs."
} finally {
    if ([System.IO.Directory]::Exists($scratch)) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
