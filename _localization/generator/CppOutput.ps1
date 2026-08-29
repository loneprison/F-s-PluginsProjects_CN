function Get-RoleType {
    param([Parameter(Mandatory = $true)][string]$Role)
    return "$($Role)Text"
}

function Get-ArrayName {
    param(
        [Parameter(Mandatory = $true)][string]$Role,
        [Parameter(Mandatory = $true)][string]$Variant
    )
    return "k$Role$Variant"
}

function New-StringTable {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$Literals
    )

    if ($Literals.Count -eq 0) {
        return $null
    }
    return Expand-GeneratorTemplate -Name 'StringTable.h.template' -Values @{
        NAME = $Name
        LITERALS = (($Literals | ForEach-Object { "    $_," }) -join "`n")
    }
}

function Get-TableInitializer {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][int]$Count
    )

    if ($Count -eq 0) {
        return '{ nullptr, 0 }'
    }
    return "{ $Name, $Count }"
}
