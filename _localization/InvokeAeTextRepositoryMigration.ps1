param(
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [Parameter(Mandatory = $true)][string]$MarkdownOutputPath,
    [string]$DetailedOutputRoot,
    [string]$ApprovedReportRoot,
    [string]$ApplyOutputRoot,
    [ValidateSet('param-label', 'popup-topic', 'special-structure')][string]$Batch,
    [switch]$Migrate
)

$ErrorActionPreference = 'Stop'
if ($Migrate) {
    if ([string]::IsNullOrWhiteSpace($ApprovedReportRoot) -or
        [string]::IsNullOrWhiteSpace($ApplyOutputRoot) -or
        [string]::IsNullOrWhiteSpace($Batch)) {
        throw '-Migrate requires ApprovedReportRoot, ApplyOutputRoot, and Batch.'
    }
    if (-not [string]::IsNullOrWhiteSpace($DetailedOutputRoot)) {
        throw '-Migrate and DetailedOutputRoot are separate operations.'
    }
} elseif (-not [string]::IsNullOrWhiteSpace($ApprovedReportRoot) -or
    -not [string]::IsNullOrWhiteSpace($ApplyOutputRoot) -or
    -not [string]::IsNullOrWhiteSpace($Batch)) {
    throw 'ApprovedReportRoot, ApplyOutputRoot, and Batch require -Migrate.'
}

$root = Split-Path -Parent $PSScriptRoot
$msbuild = 'C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe'
if (-not (Test-Path -LiteralPath $msbuild -PathType Leaf)) {
    throw 'MSBuild was not found at the validated Visual Studio location.'
}

$scratch = Join-Path ([System.IO.Path]::GetTempPath()) (
    'AeTextInventory-' + [Guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($scratch) | Out-Null
$toolsProject = Join-Path $PSScriptRoot 'tools'
$uv = (Get-Command uv.exe -ErrorAction Stop).Source
$stage7SpecialProjects = @(
    'CCplus',
    'ChannelShift',
    'ColorChangeSimple',
    'ColorKey',
    'Filter',
    'MainLineRepaint_old',
    'NamiGarasu',
    'NoiseHiLo_Alpha',
    'NoiseHiLo_RGB',
    'OpticalDiffusion',
    'OutLine'
)

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )

    $resolved = [System.IO.Path]::GetFullPath($Path)
    $parent = Split-Path -Parent $resolved
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = "$resolved.tmp.$PID.$([Guid]::NewGuid().ToString('N'))"
    try {
        $json = ($Value | ConvertTo-Json -Depth 20) + "`n"
        [System.IO.File]::WriteAllText(
            $temporary,
            $json,
            [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::Move($temporary, $resolved, $true)
    } finally {
        if ([System.IO.File]::Exists($temporary)) {
            [System.IO.File]::Delete($temporary)
        }
    }
}

function Read-InventoryManifest {
    param([Parameter(Mandatory = $true)][string]$Path)

    $project = $null
    $inputs = [System.Collections.Generic.List[string]]::new()
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        if ($line.StartsWith('PROJECT|', [System.StringComparison]::Ordinal)) {
            $fields = @($line.Substring(8).Split('|'))
            if ($fields.Count -ne 7) {
                throw "Malformed PROJECT manifest line: $Path"
            }
            $project = [pscustomobject]@{
                ProjectPath = $fields[0]
                Name = $fields[1]
                CatalogPath = $fields[2]
                Namespace = $fields[3]
                Role = $fields[4]
                Category = $fields[5]
                FamilyDefinitionPath = $fields[6]
            }
        } elseif ($line.StartsWith('COMPILE|', [System.StringComparison]::Ordinal) -or
            $line.StartsWith('INCLUDE|', [System.StringComparison]::Ordinal)) {
            $separator = $line.IndexOf('|')
            $candidate = $line.Substring($separator + 1)
            if (-not $inputs.Contains($candidate)) {
                $inputs.Add($candidate)
            }
        }
    }
    if ($null -eq $project) {
        throw "Manifest has no PROJECT record: $Path"
    }
    $project | Add-Member -NotePropertyName Inputs -NotePropertyValue @($inputs)
    return $project
}

try {
    $processPath = $env:Path
    Remove-Item Env:PATH -ErrorAction SilentlyContinue
    [Environment]::SetEnvironmentVariable('Path', $processPath, 'Process')

    $projects = @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.vcxproj' |
        Sort-Object FullName)
    for ($index = 0; $index -lt $projects.Count; $index++) {
        $manifest = Join-Path $scratch ('{0:D4}.txt' -f $index)
        & $msbuild $projects[$index].FullName `
            /t:WriteAeTextInventoryManifest `
            /p:Configuration=Debug `
            /p:Platform=x64 `
            "/p:AeTextInventoryOutput=$manifest" `
            /nologo `
            /v:quiet
        if ($LASTEXITCODE -ne 0) {
            throw "MSBuild inventory evaluation failed: $($projects[$index].FullName)"
        }
    }

    & $uv run --locked --no-dev --project $toolsProject aetext inventory `
        --manifest-directory $scratch `
        --project-root $root `
        --output ([System.IO.Path]::GetFullPath($OutputPath)) `
        --markdown-output ([System.IO.Path]::GetFullPath($MarkdownOutputPath))
    if ($LASTEXITCODE -ne 0) {
        throw "AeText repository inventory failed with exit code $LASTEXITCODE."
    }

    if ($Migrate) {
        $approvedRoot = [System.IO.Path]::GetFullPath($ApprovedReportRoot)
        $approvedSummaryPath = Join-Path $approvedRoot 'summary.json'
        if (-not (Test-Path -LiteralPath $approvedSummaryPath -PathType Leaf)) {
            throw "Approved dry-run summary does not exist: $approvedSummaryPath"
        }
        $approved = Get-Content -LiteralPath $approvedSummaryPath -Raw -Encoding UTF8 |
            ConvertFrom-Json
        if ($approved.mode -cne 'dry-run' -or $approved.writesProductFiles -or
            $approved.projectCount -ne 113 -or $approved.processedCount -ne 113) {
            throw 'Approved report is not a complete no-write 113-project dry run.'
        }

        $applyRoot = [System.IO.Path]::GetFullPath($ApplyOutputRoot)
        if ([System.IO.Directory]::Exists($applyRoot)) {
            throw "ApplyOutputRoot must not already exist: $applyRoot"
        }
        [System.IO.Directory]::CreateDirectory($applyRoot) | Out-Null

        $manifests = @{}
        foreach ($manifestPath in @(Get-ChildItem -LiteralPath $scratch -File -Filter '*.txt')) {
            $manifest = Read-InventoryManifest -Path $manifestPath.FullName
            $manifests[$manifest.Name] = $manifest
        }
        $selected = @($approved.projects | Where-Object { $_.batch -ceq $Batch })
        $expectedCount = switch ($Batch) {
            'param-label' { 64 }
            'popup-topic' { 38 }
            'special-structure' { 11 }
        }
        if ($selected.Count -ne $expectedCount) {
            throw "Approved $Batch batch has $($selected.Count) projects; expected $expectedCount."
        }

        $results = [System.Collections.Generic.List[object]]::new()
        foreach ($project in $selected) {
            $name = [string]$project.name
            $manifest = $manifests[$name]
            if ($null -eq $manifest) {
                throw "Current MSBuild inventory has no project named $name."
            }
            if ([System.IO.Path]::GetFullPath([string]$project.projectPath) -cne
                    [System.IO.Path]::GetFullPath([string]$manifest.ProjectPath) -or
                [System.IO.Path]::GetFullPath([string]$project.catalogPath) -cne
                    [System.IO.Path]::GetFullPath([string]$manifest.CatalogPath)) {
                throw "Current project or catalog path differs from the approved report: $name"
            }

            $approvedSourceList = Join-Path $approvedRoot "$name\sources.txt"
            $approvedSources = @(
                Get-Content -LiteralPath $approvedSourceList -Encoding UTF8)
            $currentSources = @($manifest.Inputs)
            if ($approvedSources.Count -ne $currentSources.Count) {
                throw "Current source-list count differs from the approved report: $name"
            }
            for ($sourceIndex = 0; $sourceIndex -lt $approvedSources.Count; $sourceIndex++) {
                if ($approvedSources[$sourceIndex] -cne $currentSources[$sourceIndex]) {
                    throw "Current source list differs from the approved report: $name"
                }
            }

            $projectOutput = Join-Path $applyRoot $name
            [System.IO.Directory]::CreateDirectory($projectOutput) | Out-Null
            $contentApplied = $false
            $contentSkipped = -not [bool]$project.readyForBindingRemoval
            $projectViewApplied = $false
            $projectViewIdempotent = $name -ceq 'AlphaFix'
            $errors = [System.Collections.Generic.List[string]]::new()

            if (-not $contentSkipped) {
                try {
                    $approvedEquivalence = [System.IO.Path]::GetFullPath(
                        [string]$project.equivalencePath)
                    if (-not $approvedEquivalence.StartsWith(
                        $approvedRoot + [System.IO.Path]::DirectorySeparatorChar,
                        [System.StringComparison]::OrdinalIgnoreCase)) {
                        throw "Equivalence report is outside ApprovedReportRoot: $name"
                    }
                    & (Join-Path $PSScriptRoot 'MigrateTextCatalog.ps1') `
                        -InputPath $manifest.CatalogPath `
                        -SourceListPath $approvedSourceList `
                        -FamilyDefinitionPath $manifest.FamilyDefinitionPath `
                        -Namespace $manifest.Namespace `
                        -ProjectRoot $root `
                        -OutputPath (Join-Path $projectOutput 'migration-apply.json') `
                        -EquivalenceReport $approvedEquivalence `
                        -Migrate
                    $contentApplied = $true
                } catch {
                    $errors.Add("content: $($_.Exception.Message)")
                }
            }

            if ($name -cne 'AlphaFix') {
                try {
                    $projectViewPath = Join-Path $projectOutput 'project-view-apply.json'
                    & $uv run --locked --no-dev --project $toolsProject aetext `
                        sync-project-view `
                        --repository $root `
                        --project $name `
                        --output $projectViewPath `
                        --apply
                    if ($LASTEXITCODE -ne 0) {
                        throw "sync-project-view apply failed with exit code $LASTEXITCODE."
                    }
                    $projectView = Get-Content -LiteralPath $projectViewPath -Raw -Encoding UTF8 |
                        ConvertFrom-Json
                    $projectViewApplied = [bool]$projectView.applied

                    $idempotencePath = Join-Path $projectOutput 'project-view-second-run.json'
                    & $uv run --locked --no-dev --project $toolsProject aetext `
                        sync-project-view `
                        --repository $root `
                        --project $name `
                        --output $idempotencePath
                    if ($LASTEXITCODE -ne 0) {
                        throw "sync-project-view second run failed with exit code $LASTEXITCODE."
                    }
                    $idempotence = Get-Content -LiteralPath $idempotencePath `
                        -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($idempotence.changed) {
                        throw 'sync-project-view second run reported changed=true.'
                    }
                    $projectViewIdempotent = $true
                } catch {
                    $errors.Add("project-view: $($_.Exception.Message)")
                }
            }

            $results.Add([pscustomobject]@{
                name = $name
                readyForBindingRemoval = [bool]$project.readyForBindingRemoval
                contentApplied = $contentApplied
                contentSkipped = $contentSkipped
                projectViewApplied = $projectViewApplied
                projectViewIdempotent = $projectViewIdempotent
                errors = @($errors)
            })
            Write-JsonFile -Path (Join-Path $applyRoot 'summary.json') -Value ([ordered]@{
                schemaVersion = 1
                mode = 'apply'
                batch = $Batch
                approvedSummarySha256 = (
                    Get-FileHash -LiteralPath $approvedSummaryPath -Algorithm SHA256).Hash
                selectedCount = $selected.Count
                processedCount = $results.Count
                contentAppliedCount = @($results | Where-Object contentApplied).Count
                contentSkippedCount = @($results | Where-Object contentSkipped).Count
                projectViewIdempotentCount = @(
                    $results | Where-Object projectViewIdempotent).Count
                errorCount = @($results | Where-Object { $_.errors.Count -gt 0 }).Count
                projects = @($results)
            })
        }

        $failed = @($results | Where-Object { $_.errors.Count -gt 0 })
        Write-Host "AeText $Batch apply: $($results.Count) processed, " `
            "$(@($results | Where-Object contentApplied).Count) content migrations, " `
            "$(@($results | Where-Object contentSkipped).Count) approved skips, " `
            "$($failed.Count) errors."
        if ($failed.Count -gt 0) {
            exit 1
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($DetailedOutputRoot)) {
        $details = [System.IO.Path]::GetFullPath($DetailedOutputRoot)
        if ([System.IO.Directory]::Exists($details)) {
            throw "DetailedOutputRoot must not already exist: $details"
        }
        [System.IO.Directory]::CreateDirectory($details) | Out-Null

        $inventory = Get-Content -LiteralPath ([System.IO.Path]::GetFullPath($OutputPath)) `
            -Raw -Encoding UTF8 | ConvertFrom-Json
        $inventoryByName = @{}
        foreach ($project in @($inventory.projects)) {
            $inventoryByName[[string]$project.name] = $project
        }
        $manifests = @{}
        foreach ($manifestPath in @(Get-ChildItem -LiteralPath $scratch -File -Filter '*.txt')) {
            $manifest = Read-InventoryManifest -Path $manifestPath.FullName
            $manifests[$manifest.Name] = $manifest
        }
        $current = @($inventory.projects | Where-Object {
            $_.catalogState -ceq 'legacy-bindings' -and $_.name -cne 'NFsSkelton'
        })
        if ($current.Count -ne 113) {
            throw "Expected 113 current F's legacy effects, found $($current.Count)."
        }

        $results = [System.Collections.Generic.List[object]]::new()
        foreach ($inventoryProject in $current) {
            $name = [string]$inventoryProject.name
            $manifest = $manifests[$name]
            # Preserve the risk partition from the first complete no-write inventory. Adding a
            # previously omitted entry header to @(ClInclude) must not silently lower its batch.
            $batch = if ($stage7SpecialProjects -ccontains $name) {
                'special-structure'
            } elseif ($inventoryProject.risk.popupTopic) {
                'popup-topic'
            } else {
                'param-label'
            }
            $projectOutput = Join-Path $details $name
            [System.IO.Directory]::CreateDirectory($projectOutput) | Out-Null
            $sourceList = Join-Path $projectOutput 'sources.txt'
            [System.IO.File]::WriteAllLines(
                $sourceList,
                [string[]]$manifest.Inputs,
                [System.Text.UTF8Encoding]::new($false))
            $planPath = Join-Path $projectOutput 'migration-plan.json'
            $prospective = Join-Path $projectOutput 'prospective'
            $baselineHeader = Join-Path $projectOutput 'legacy.generated.h'
            $baselineBinding = Join-Path $projectOutput 'legacy.bindings.json'
            $prospectiveHeader = Join-Path $prospective 'prospective.generated.h'
            $prospectiveBinding = Join-Path $prospective 'prospective.bindings.json'
            $equivalencePath = Join-Path $projectOutput 'equivalence.json'
            $errors = [System.Collections.Generic.List[string]]::new()
            $ready = $false

            try {
                & (Join-Path $PSScriptRoot 'GenerateTextCatalog.ps1') `
                    -InputPath $manifest.CatalogPath `
                    -OutputPath $baselineHeader `
                    -Namespace $manifest.Namespace `
                    -Kind Effect `
                    -SourceListPath $sourceList `
                    -BindingReportPath $baselineBinding `
                    -ProjectRoot $root `
                    -FamilyDefinitionPath $manifest.FamilyDefinitionPath

                & (Join-Path $PSScriptRoot 'MigrateTextCatalog.ps1') `
                    -InputPath $manifest.CatalogPath `
                    -SourceListPath $sourceList `
                    -FamilyDefinitionPath $manifest.FamilyDefinitionPath `
                    -Namespace $manifest.Namespace `
                    -ProjectRoot $root `
                    -OutputPath $planPath `
                    -ProspectiveDirectory $prospective

                $prospectiveData = Get-Content -LiteralPath $planPath -Raw -Encoding UTF8 |
                    ConvertFrom-Json
                & (Join-Path $PSScriptRoot 'GenerateTextCatalog.ps1') `
                    -InputPath $prospectiveData.prospectiveWorkspace.catalogPath `
                    -OutputPath $prospectiveHeader `
                    -Namespace $manifest.Namespace `
                    -Kind Effect `
                    -SourceListPath $prospectiveData.prospectiveWorkspace.sourceListPath `
                    -BindingReportPath $prospectiveBinding `
                    -ProjectRoot $prospective `
                    -FamilyDefinitionPath $manifest.FamilyDefinitionPath

                & $uv run --locked --no-dev --project $toolsProject aetext compare `
                    --baseline "$baselineBinding.bytes.json" `
                    --generated-bytes "$prospectiveBinding.bytes.json" `
                    --generated-bindings $prospectiveBinding `
                    --migration-report $planPath `
                    --legacy-catalog $manifest.CatalogPath `
                    --prospective-catalog $prospectiveData.prospectiveWorkspace.catalogPath `
                    --output $equivalencePath
                $compareExit = $LASTEXITCODE
                $equivalence = Get-Content -LiteralPath $equivalencePath -Raw -Encoding UTF8 |
                    ConvertFrom-Json
                $ready = $compareExit -eq 0 -and $equivalence.readyForBindingRemoval
            } catch {
                $errors.Add($_.Exception.Message)
            }

            $results.Add([pscustomobject]@{
                name = $name
                batch = $batch
                projectPath = [string]$inventoryProject.projectPath
                catalogPath = [string]$inventoryProject.catalogPath
                planPath = $planPath
                prospectivePath = $prospective
                equivalencePath = $equivalencePath
                readyForBindingRemoval = [bool]$ready
                errors = @($errors)
            })
            Write-JsonFile -Path (Join-Path $details 'summary.json') -Value ([ordered]@{
                schemaVersion = 1
                mode = 'dry-run'
                writesProductFiles = $false
                projectCount = 113
                processedCount = $results.Count
                greenCount = @($results | Where-Object readyForBindingRemoval).Count
                redCount = @($results | Where-Object { -not $_.readyForBindingRemoval }).Count
                projects = @($results)
            })
        }

        $green = @($results | Where-Object readyForBindingRemoval)
        $red = @($results | Where-Object { -not $_.readyForBindingRemoval })
        Write-Host "AeText detailed migration dry run: 113 processed, $($green.Count) green, $($red.Count) red."
        if ($red.Count -gt 0) {
            exit 1
        }
    }
} finally {
    if (Test-Path -LiteralPath $scratch) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
