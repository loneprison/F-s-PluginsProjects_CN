function Read-JsonObjectFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Name
    )

    $resolved = (Resolve-Path -LiteralPath $Path).Path
    $value = Get-Content -LiteralPath $resolved -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Object -Value $value -Name $Name
    return $value
}

function Read-FamilyDefinition {
    $family = Read-JsonObjectFile -Path $FamilyDefinitionPath -Name 'Family definition'
    Assert-Properties -Value $family -Allowed @(
        'schemaVersion', 'familyId', 'sourceVariantId', 'variants') -Name 'family'
    if ($family.schemaVersion -ne 1) {
        throw 'family.schemaVersion must be 1.'
    }
    [void](Get-RequiredString -Value $family -Property 'familyId' -Name 'family')
    $sourceVariantId = Get-RequiredString -Value $family -Property 'sourceVariantId' -Name 'family'
    if ($family.variants -isnot [object[]] -or $family.variants.Count -eq 0) {
        throw 'family.variants must be a non-empty array.'
    }

    $variantIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $translationLocales = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $sourceCount = 0
    foreach ($variant in @($family.variants)) {
        Assert-Object -Value $variant -Name 'family variant'
        Assert-Properties -Value $variant -Allowed @(
            'id', 'textSource', 'encodingProfile') -Name 'family variant'
        $id = Get-RequiredString -Value $variant -Property 'id' -Name 'family variant'
        if ($id -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$' -or -not $variantIds.Add($id)) {
            throw "Invalid or duplicate family Variant ID: $id"
        }
        $profile = Get-RequiredString -Value $variant -Property 'encodingProfile' -Name "family variant $id"
        if (-not (@('windows-1252', 'windows-932', 'windows-936', 'windows-936-ae-display') -ccontains $profile)) {
            throw "Unsupported encoding profile: variant=$id profile=$profile"
        }
        Assert-Object -Value $variant.textSource -Name "family variant $id.textSource"
        $kind = Get-RequiredString -Value $variant.textSource -Property 'kind' -Name "family variant $id.textSource"
        if ($kind -ceq 'source') {
            Assert-Properties -Value $variant.textSource -Allowed @('kind') -Name "family variant $id.textSource"
            if ($id -ceq $sourceVariantId) {
                $sourceCount++
            }
        } elseif ($kind -ceq 'translation') {
            Assert-Properties -Value $variant.textSource -Allowed @('kind', 'locale') -Name "family variant $id.textSource"
            $locale = Get-RequiredString -Value $variant.textSource -Property 'locale' -Name "family variant $id.textSource"
            if ($locale -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') {
                throw "Invalid family translation locale: $locale"
            }
            [void]$translationLocales.Add($locale)
        } else {
            throw "Unsupported family text source kind: variant=$id kind=$kind"
        }
    }
    if (-not $variantIds.Contains($sourceVariantId) -or $sourceCount -ne 1) {
        throw 'family.sourceVariantId must name exactly one source Variant.'
    }
    return [pscustomobject]@{
        Definition = $family
        TranslationLocales = @($translationLocales | Sort-Object)
    }
}

function Read-RuntimeIdentity {
    $identity = Read-JsonObjectFile -Path $RuntimeIdentityPath -Name 'Runtime identity'
    Assert-Properties -Value $identity -Allowed @('schemaVersion', 'suite', 'config') -Name 'runtime identity'
    if ($identity.schemaVersion -ne 1) {
        throw 'runtime identity.schemaVersion must be 1.'
    }
    Assert-Object -Value $identity.suite -Name 'runtime identity.suite'
    Assert-Properties -Value $identity.suite -Allowed @(
        'name', 'version', 'internalVersion') -Name 'runtime identity.suite'
    [void](Get-RequiredString -Value $identity.suite -Property 'name' -Name 'runtime identity.suite')
    foreach ($property in @('version', 'internalVersion')) {
        $value = $identity.suite.$property
        if (($value -isnot [int] -and $value -isnot [long]) -or
            $value -le 0 -or $value -gt [int]::MaxValue) {
            throw "runtime identity.suite.$property must be a positive integer."
        }
    }
    Assert-Object -Value $identity.config -Name 'runtime identity.config'
    Assert-Properties -Value $identity.config -Allowed @(
        'directoryName', 'fileName', 'invalidBackupFileName', 'mutexName') -Name 'runtime identity.config'
    foreach ($property in @('directoryName', 'fileName', 'invalidBackupFileName', 'mutexName')) {
        [void](Get-RequiredString -Value $identity.config -Property $property -Name 'runtime identity.config')
    }
    return $identity
}

function Convert-ToCppNarrowLiteral {
    param([Parameter(Mandatory = $true)][string]$Value)

    $builder = [System.Text.StringBuilder]::new('"')
    foreach ($character in $Value.ToCharArray()) {
        $code = [int]$character
        if ($character -eq '"') {
            [void]$builder.Append('\"')
        } elseif ($character -eq '\') {
            [void]$builder.Append('\\')
        } elseif ($code -ge 0x20 -and $code -le 0x7e) {
            [void]$builder.Append($character)
        } else {
            throw 'Runtime suite name must contain printable ASCII only.'
        }
    }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function Get-VariantSymbol {
    param([Parameter(Mandatory = $true)][string]$Id)
    return [regex]::Replace($Id, '[^A-Za-z0-9_]', '_')
}

function Convert-VariantBytes {
    param(
        [Parameter(Mandatory = $true)][string]$Value,
        [Parameter(Mandatory = $true)][string]$Profile,
        [Parameter(Mandatory = $true)][string]$Id
    )

    switch ($Profile) {
        'windows-1252' {
            return Convert-ToTargetBytes -Value $Value -Encoding (Get-StrictEncoding -CodePage 1252) -Target 'CP1252' -Id $Id
        }
        'windows-932' {
            return Convert-ToTargetBytes -Value $Value -Encoding (Get-StrictEncoding -CodePage 932) -Target 'CP932' -Id $Id
        }
        'windows-936' {
            return Convert-ToTargetBytes -Value $Value -Encoding (Get-StrictEncoding -CodePage 936) -Target 'CP936' -Id $Id
        }
        'windows-936-ae-display' {
            return Convert-ToTargetBytes -Value $Value -Encoding (Get-StrictEncoding -CodePage 936) -Target 'windows-936-ae-display' -Id $Id -AeDisplayProfile
        }
        default {
            throw "Unsupported encoding profile: $Profile"
        }
    }
}
