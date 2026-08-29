$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$project = Join-Path $root 'PluginSkeleton\Win\PluginSkeleton.vcxproj'
$legacyProject = Join-Path $root 'AlphaFix\Win\AlphaFix.vcxproj'
$settingsProject = Join-Path $root 'LanguageSettings\Win\FsLanguageSettings.vcxproj'
$clientSource = Join-Path $root '_localization\core\AeTextClient.cpp'
$filters = $project + '.filters'
$targets = Join-Path $root '_localization\AeText.Build.targets'
$solution = Join-Path $root "F's PluginsProjects.slnx"

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
    throw 'Visual Studio Installer vswhere.exe was not found.'
}

$installation = & $vswhere `
    -latest `
    -products * `
    -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
    -property installationPath
if (-not $installation) {
    throw 'A Visual Studio installation with the x64 C++ tools was not found.'
}

$msbuild = Join-Path $installation 'MSBuild\Current\Bin\MSBuild.exe'
if (-not (Test-Path -LiteralPath $msbuild -PathType Leaf)) {
    throw "MSBuild was not found: $msbuild"
}

$processPath = $env:Path
Remove-Item Env:PATH -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable('Path', $processPath, 'Process')

$scratch = Join-Path ([System.IO.Path]::GetTempPath()) (
    'AeTextProjectIntegration-' + [Guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($scratch) | Out-Null

function Invoke-MsBuildJson {
    param(
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $true)][string]$GetItem,
        [Parameter(Mandatory = $true)][string]$IntermediateDirectory
    )

    $arguments = @(
        $project,
        '-nologo',
        "-target:$Target",
        '-property:Configuration=Debug',
        '-property:Platform=x64',
        '-property:DesignTimeBuild=true',
        '-property:BuildingInsideVisualStudio=true',
        '-property:SkipCompilerExecution=true',
        "-property:IntDir=$IntermediateDirectory\",
        "-getItem:$GetItem"
    )
    $output = & $msbuild @arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Design-time target $Target failed:`n$($output -join [Environment]::NewLine)"
    }
    return (($output -join [Environment]::NewLine) | ConvertFrom-Json)
}

function Get-ClCompilePaths {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath
    )

    $arguments = @(
        $ProjectPath,
        '-nologo',
        '-property:Configuration=Debug',
        '-property:Platform=x64',
        '-getItem:ClCompile'
    )
    $output = & $msbuild @arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "ClCompile evaluation failed for ${ProjectPath}:`n$($output -join [Environment]::NewLine)"
    }
    $result = (($output -join [Environment]::NewLine) | ConvertFrom-Json)
    return @($result.Items.ClCompile | ForEach-Object {
        [System.IO.Path]::GetFullPath($_.FullPath)
    })
}

try {
    $normalizedClientSource = [System.IO.Path]::GetFullPath($clientSource)
    $clientIntegrationCases = @(
        @{ Name = 'legacy effect'; Project = $legacyProject; Expected = 1 },
        @{ Name = 'source-derived effect'; Project = $project; Expected = 1 },
        @{ Name = 'Settings support'; Project = $settingsProject; Expected = 0 }
    )
    foreach ($case in $clientIntegrationCases) {
        $compilePaths = @(Get-ClCompilePaths -ProjectPath $case.Project)
        $clientCount = @($compilePaths | Where-Object { $_ -eq $normalizedClientSource }).Count
        if ($clientCount -ne $case.Expected) {
            throw "$($case.Name) must compile AeTextClient.cpp exactly $($case.Expected) time(s); found $clientCount in $($case.Project)."
        }
    }

    $designTimeIntDir = Join-Path $scratch 'design-time'
    $commandLines = Invoke-MsBuildJson `
        -Target 'GetClCommandLines' `
        -GetItem 'ClCommandLines' `
        -IntermediateDirectory $designTimeIntDir

    $localizationDirectory = Join-Path $designTimeIntDir 'Localization'
    $generatedHeader = Join-Path $localizationDirectory 'PluginSkeletonText.generated.h'
    $sourceList = Join-Path $localizationDirectory 'PluginSkeletonText.sources.txt'
    if (-not (Test-Path -LiteralPath $generatedHeader -PathType Leaf)) {
        throw "Design-time generation did not create the generated header: $generatedHeader"
    }
    if (-not (Test-Path -LiteralPath $sourceList -PathType Leaf)) {
        throw "Design-time generation did not create the source list: $sourceList"
    }

    $sourcePaths = @(Get-Content -LiteralPath $sourceList)
    $missingSourcePaths = @($sourcePaths | Where-Object {
        -not (Test-Path -LiteralPath $_ -PathType Leaf)
    })
    if ($missingSourcePaths.Count -ne 0) {
        throw "Design-time source list contains nonexistent paths: $($missingSourcePaths -join '; ')"
    }
    if (@($sourcePaths | Where-Object { $_ -like '*\__temporary.cpp' }).Count -ne 0) {
        throw 'Design-time source list contains the Visual Studio synthetic __temporary.cpp item.'
    }

    $commandLineItems = @($commandLines.Items.ClCommandLines)
    if ($commandLineItems.Count -eq 0) {
        throw 'GetClCommandLines returned no compiler command line.'
    }
    $normalizedGeneratedInclude = $localizationDirectory.TrimEnd('\')
    if (-not ($commandLineItems[0].Identity -like "*$normalizedGeneratedInclude*")) {
        throw "The design-time compiler command line does not contain the generated include path: $normalizedGeneratedInclude"
    }

    $generatedFiles = Invoke-MsBuildJson `
        -Target 'GetGeneratedFiles' `
        -GetItem '_GeneratedFiles,GeneratedFilesOutputGroup' `
        -IntermediateDirectory $designTimeIntDir
    $reportedGeneratedFiles = @($generatedFiles.Items._GeneratedFiles | ForEach-Object {
        [System.IO.Path]::GetFullPath($_.FullPath)
    })
    if ($reportedGeneratedFiles -notcontains [System.IO.Path]::GetFullPath($generatedHeader)) {
        throw 'GetGeneratedFiles did not report PluginSkeletonText.generated.h.'
    }

    [xml]$projectXml = Get-Content -Raw -LiteralPath $project
    [xml]$filtersXml = Get-Content -Raw -LiteralPath $filters
    $namespace = New-Object System.Xml.XmlNamespaceManager($projectXml.NameTable)
    $namespace.AddNamespace('m', $projectXml.DocumentElement.NamespaceURI)
    $filterNamespace = New-Object System.Xml.XmlNamespaceManager($filtersXml.NameTable)
    $filterNamespace.AddNamespace('m', $filtersXml.DocumentElement.NamespaceURI)

    $requiredItems = @(
        @{ Kind = 'None'; Include = '..\..\_localization\catalog\(Templates)\PluginSkeleton.json' },
        @{ Kind = 'ClInclude'; Include = '..\..\_localization\AeText.h' },
        @{ Kind = 'ClCompile'; Include = '..\..\_localization\core\AeTextClient.cpp' }
    )
    foreach ($requiredItem in $requiredItems) {
        $projectNode = $projectXml.SelectSingleNode(
            "//m:$($requiredItem.Kind)[@Include='$($requiredItem.Include)']", $namespace)
        if ($null -eq $projectNode) {
            throw "PluginSkeleton.vcxproj does not list $($requiredItem.Include) as $($requiredItem.Kind)."
        }
        $filterNode = $filtersXml.SelectSingleNode(
            "//m:$($requiredItem.Kind)[@Include='$($requiredItem.Include)']/m:Filter", $filterNamespace)
        if ($null -eq $filterNode -or $filterNode.InnerText -ne 'Localization') {
            throw "PluginSkeleton.vcxproj.filters does not place $($requiredItem.Include) in Localization."
        }
    }

    [xml]$solutionXml = Get-Content -Raw -LiteralPath $solution
    $requiredInfrastructureFiles = @(
        '_localization/families/fs/generation.json',
        '_localization/families/fs/review-workflow.json',
        '_localization/families/fs/runtime-identity.json',
        '_localization/generator/EffectGenerator.ps1',
        '_localization/tools/src/aetext/catalog/source_index.py',
        '_localization/tools/src/aetext/catalog/workflow.py',
        '_localization/tools/src/aetext/classification.py',
        '_localization/tools/src/aetext/legacy_retirement.py',
        '_localization/tools/src/aetext/scanner.py',
        '_localization/tools/src/aetext/web/project_tree.py',
        '_localization/tools/src/aetext/web/translation_grid.py',
        '_localization/tools/src/aetext/web/workflow_settings.py',
        '_localization/tools/tests/unit/test_classification.py',
        '_localization/tools/tests/unit/test_legacy_retirement.py',
        '_localization/tests/ValidateAeTextProjectIntegration.ps1'
    )
    foreach ($infrastructureFile in $requiredInfrastructureFiles) {
        $nodes = @($solutionXml.SelectNodes(
            "//Folder[starts-with(@Name, '/AeText Infrastructure/')]/File[@Path='$infrastructureFile']"))
        if ($nodes.Count -ne 1) {
            throw "The solution must list $infrastructureFile exactly once under AeText Infrastructure."
        }
    }

    $projectOwnedSolutionItems = @(
        '_localization/catalog/(Templates)/PluginSkeleton.json',
        '_localization/AeText.h',
        '_localization/core/AeTextClient.cpp'
    )
    foreach ($projectOwnedSolutionItem in $projectOwnedSolutionItems) {
        if ($null -ne $solutionXml.SelectSingleNode("//File[@Path='$projectOwnedSolutionItem']")) {
            throw "The project-owned item $projectOwnedSolutionItem must not be duplicated in the solution infrastructure view."
        }
    }

    [xml]$targetsXml = Get-Content -Raw -LiteralPath $targets
    $targetsNamespace = New-Object System.Xml.XmlNamespaceManager($targetsXml.NameTable)
    $targetsNamespace.AddNamespace('m', $targetsXml.DocumentElement.NamespaceURI)
    $implicitClient = $targetsXml.SelectSingleNode(
        "//m:ClCompile[@Include='`$(AeTextClientSource)']", $targetsNamespace)
    if ($null -ne $implicitClient) {
        throw 'AeText.Build.targets still injects AeTextClient.cpp implicitly.'
    }

    $missingSource = Join-Path $scratch 'missing-real-source.cpp'
    $injection = Join-Path $scratch 'inject-missing-source.targets'
    $injectionXml = @"
<?xml version="1.0" encoding="utf-8"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <ClCompile Include="$missingSource" />
  </ItemGroup>
</Project>
"@
    [System.IO.File]::WriteAllText(
        $injection, $injectionXml, [System.Text.UTF8Encoding]::new($false))

    $ordinaryIntDir = Join-Path $scratch 'ordinary-missing-source'
    $ordinaryOutput = & $msbuild `
        $project `
        '-nologo' `
        '-target:GenerateAeTextCatalog' `
        '-property:Configuration=Debug' `
        '-property:Platform=x64' `
        "-property:IntDir=$ordinaryIntDir\" `
        "-property:ForceImportAfterCppTargets=$injection" `
        '-verbosity:minimal' 2>&1
    if ($LASTEXITCODE -eq 0) {
        throw 'An ordinary generation unexpectedly accepted a nonexistent real ClCompile item.'
    }
    if (($ordinaryOutput -join [Environment]::NewLine) -notlike '*missing-real-source.cpp*') {
        throw "The ordinary generation failure did not identify the missing real source:`n$($ordinaryOutput -join [Environment]::NewLine)"
    }

    'AeText project integration validation passed.'
} finally {
    if (Test-Path -LiteralPath $scratch) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
