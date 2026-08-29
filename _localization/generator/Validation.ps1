function Add-Issue {
    param([Parameter(Mandatory = $true)][string]$Message)

    $issues.Add($Message)
    if (-not $PublicationValidation) {
        Write-Warning "localization: $Message"
    }
}

function Assert-Object {
    param(
        [Parameter(Mandatory = $true)][object]$Value,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($Value -isnot [System.Management.Automation.PSCustomObject]) {
        throw "$Name must be an object."
    }
}

function Assert-Properties {
    param(
        [Parameter(Mandatory = $true)][object]$Value,
        [Parameter(Mandatory = $true)][string[]]$Allowed,
        [Parameter(Mandatory = $true)][string]$Name
    )

    foreach ($property in $Value.PSObject.Properties) {
        if (-not ($Allowed -ccontains $property.Name)) {
            throw "Unsupported property: $Name.$($property.Name)"
        }
    }
}

function Get-RequiredString {
    param(
        [Parameter(Mandatory = $true)][object]$Value,
        [Parameter(Mandatory = $true)][string]$Property,
        [Parameter(Mandatory = $true)][string]$Name
    )

    $item = $Value.PSObject.Properties[$Property]
    if ($null -eq $item -or $item.Value -isnot [string] -or $item.Value.Length -eq 0) {
        throw "$Name.$Property must be a non-empty string."
    }
    return [string]$item.Value
}

function Get-OptionalString {
    param(
        [Parameter(Mandatory = $true)][object]$Value,
        [Parameter(Mandatory = $true)][string]$Property,
        [Parameter(Mandatory = $true)][string]$Fallback,
        [Parameter(Mandatory = $true)][string]$Language,
        [Parameter(Mandatory = $true)][string]$Id
    )

    $item = $Value.PSObject.Properties[$Property]
    if ($null -eq $item) {
        Add-Issue "Missing translation: language=$Language id=$Id"
        return $Fallback
    }
    if ($item.Value -isnot [string]) {
        throw "Translation must be a string: language=$Language id=$Id"
    }
    if ($item.Value.Length -eq 0) {
        Add-Issue "Missing translation: language=$Language id=$Id"
        return $Fallback
    }
    return [string]$item.Value
}

function Get-Placeholders {
    param([Parameter(Mandatory = $true)][string]$Value)

    $placeholders = @(
        [regex]::Matches($Value, '\{[A-Za-z_][A-Za-z0-9_]*\}') |
            ForEach-Object { $_.Value }
        [regex]::Matches($Value, "%(?:\d+\$)?[-+ #0']*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn]") |
            ForEach-Object { "printf:$($_.Value)" }
    )
    return @($placeholders | Sort-Object)
}

function Assert-Placeholders {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Language,
        [Parameter(Mandatory = $true)][string]$Original,
        [Parameter(Mandatory = $true)][string]$Translation
    )

    $expected = @(Get-Placeholders -Value $Original)
    $actual = @(Get-Placeholders -Value $Translation)
    if (($expected -join "`n") -ne ($actual -join "`n")) {
        throw "Placeholder mismatch: language=$Language id=$Id expected=[$($expected -join ', ')] actual=[$($actual -join ', ')]"
    }
}
