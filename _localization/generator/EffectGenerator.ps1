function Sort-EffectEntriesOrdinal {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [object[]]$Entries
    )

    $result = [System.Collections.Generic.List[object]]::new()
    foreach ($entry in $Entries) {
        $position = 0
        while ($position -lt $result.Count -and
            [System.StringComparer]::Ordinal.Compare([string]$result[$position].id, [string]$entry.id) -le 0) {
            $position++
        }
        $result.Insert($position, $entry)
    }
    return @($result)
}

function Get-TranslationValue {
    param(
        [Parameter(Mandatory = $true)][object]$Map,
        [Parameter(Mandatory = $true)][string]$Locale,
        [Parameter(Mandatory = $true)][object]$Record
    )

    $property = $Map.PSObject.Properties[$Record.id]
    if ($null -eq $property) {
        Add-Issue "Missing translation: language=$Locale id=$($Record.id)"
        return $Record.original
    }
    if ($null -eq $property.Value) {
        Add-Issue "Missing translation: language=$Locale id=$($Record.id)"
        return $Record.original
    }
    if ($property.Value -is [string]) {
        if ($property.Value.Length -eq 0) {
            Add-Issue "Missing translation: language=$Locale id=$($Record.id)"
            return $Record.original
        }
        return [string]$property.Value
    }
    if ($property.Value -is [System.Management.Automation.PSCustomObject]) {
        Assert-Properties -Value $property.Value -Allowed @('useSource') -Name "translation $Locale.$($Record.id)"
        if ($property.Value.useSource -is [bool] -and $property.Value.useSource) {
            return $Record.original
        }
    }
    throw "Translation must be a non-empty string, null, or exact useSource object: language=$Locale id=$($Record.id)"
}

function Write-EffectHeader {
    param(
        [Parameter(Mandatory = $true)][object]$Root,
        [Parameter(Mandatory = $true)][object]$BindingModel,
        [Parameter(Mandatory = $true)][object]$SourceMacros,
        [Parameter(Mandatory = $true)][object]$Family,
        [Parameter(Mandatory = $true)][string[]]$TranslationLocales,
        [Parameter(Mandatory = $true)][AllowNull()][object]$RuntimeIdentity,
        [string]$DefaultVariantId,
        [switch]$SingleLanguage
    )

    $resolvedDefaultVariantId = if ([string]::IsNullOrWhiteSpace($DefaultVariantId)) {
        [string]$Family.sourceVariantId
    } else {
        $DefaultVariantId
    }
    $defaultVariants = @($Family.variants | Where-Object {
        [string]$_.id -ceq $resolvedDefaultVariantId
    })
    if ($defaultVariants.Count -ne 1) {
        throw "Default Variant does not exist in the family definition: $resolvedDefaultVariantId"
    }
    $generatedVariants = @(if ($SingleLanguage) {
        $defaultVariants[0]
    } else {
        $Family.variants
    })

    Assert-Properties -Value $Root -Allowed $TranslationLocales -Name 'catalog.translations'
    $translationMaps = @{}
    foreach ($locale in $TranslationLocales) {
        $property = $Root.PSObject.Properties[$locale]
        if ($null -eq $property) {
            throw "catalog.translations.$locale must be an object."
        }
        Assert-Object -Value $property.Value -Name "catalog.translations.$locale"
        $translationMaps[$locale] = $property.Value
    }

    $roles = @('Param', 'Label', 'Popup', 'Topic', 'About', 'Error')
    $entriesByRole = [ordered]@{}
    foreach ($role in $roles) {
        $entriesByRole[$role] = [System.Collections.Generic.List[object]]::new()
    }
    $recordsById = [ordered]@{}
    foreach ($entry in @($BindingModel.entries)) {
        $id = [string]$entry.id
        $source = [string]$entry.source
        $role = [string]$entry.role
        $disposition = [string]$entry.disposition
        $original = $SourceMacros.Values[$source]

        $record = [pscustomobject]@{
            id = $id
            role = $role
            source = $source
            source_file = $SourceMacros.SourceFiles[$source]
            original = $original
            disposition = $disposition
            texts = if ($recordsById.Contains($id)) { $recordsById[$id].texts } else { @{} }
            legacyHex = [ordered]@{}
            utf8Hex = [ordered]@{}
        }
        if (-not $recordsById.Contains($id)) {
            $recordsById[$id] = $record
        }
        $entriesByRole[$role].Add($record)
    }

    foreach ($role in $roles) {
        $sorted = @(Sort-EffectEntriesOrdinal -Entries @($entriesByRole[$role]))
        $entriesByRole[$role].Clear()
        foreach ($entry in $sorted) {
            $entriesByRole[$role].Add($entry)
        }
    }

    foreach ($locale in $TranslationLocales) {
        foreach ($property in $translationMaps[$locale].PSObject.Properties) {
            $id = $property.Name
            if (-not $recordsById.Contains($id)) {
                throw "Translation has no effect binding: language=$locale id=$id"
            }
            if ($recordsById[$id].disposition -eq 'verbatim') {
                throw "Verbatim binding must not have translations: language=$locale id=$id"
            }
        }
    }

    $popupIds = @($entriesByRole['Popup'] | ForEach-Object { $_.id })
    foreach ($record in $recordsById.Values) {
        foreach ($variant in $generatedVariants) {
            $kind = [string]$variant.textSource.kind
            if ($record.disposition -eq 'verbatim' -or $kind -eq 'source') {
                $record.texts[[string]$variant.id] = $record.original
            } else {
                $locale = [string]$variant.textSource.locale
                $record.texts[[string]$variant.id] = Get-TranslationValue `
                    -Map $translationMaps[$locale] -Locale $locale -Record $record
            }
        }
        foreach ($variant in $generatedVariants) {
            if ($record.disposition -eq 'translated' -and
                [string]$variant.textSource.kind -eq 'translation') {
                $locale = [string]$variant.textSource.locale
                $translated = [string]$record.texts[[string]$variant.id]
                Assert-Placeholders -Id $record.id -Language $locale `
                    -Original $record.original -Translation $translated
                if ($popupIds -ccontains $record.id) {
                    $originalItems = @([regex]::Split($record.original, '\|'))
                    $items = @([regex]::Split($translated, '\|'))
                    if ($items.Count -ne $originalItems.Count) {
                        throw "Popup structure mismatch: id=$($record.id) expected_items=$($originalItems.Count)"
                    }
                    for ($index = 0; $index -lt $originalItems.Count; $index++) {
                        if (($originalItems[$index].Length -eq 0) -ne ($items[$index].Length -eq 0)) {
                            throw "Popup empty-item structure mismatch: id=$($record.id) item=$index"
                        }
                        if (($originalItems[$index] -ceq '(-') -ne ($items[$index] -ceq '(-')) {
                            throw "Popup separator structure mismatch: id=$($record.id) item=$index"
                        }
                    }
                }
            }
        }
    }

    $encoded = @{}
    $aboutUtf8 = @{}
    $errorUtf8 = @{}
    foreach ($variant in $generatedVariants) {
        $variantId = [string]$variant.id
        $encoded[$variantId] = @{}
        foreach ($role in $roles) {
            $encoded[$variantId][$role] = [System.Collections.Generic.List[string]]::new()
            foreach ($record in $entriesByRole[$role]) {
                $bytes = Convert-VariantBytes `
                    -Value ([string]$record.texts[$variantId]) `
                    -Profile ([string]$variant.encodingProfile) `
                    -Id $record.id
                $limit = if ($role -in @('Param', 'Topic')) { 31 } else { 255 }
                Assert-ByteLimit -Bytes $bytes -Limit $limit -Target $variantId -Id $record.id
                $encoded[$variantId][$role].Add((Convert-ToByteLiteral -Bytes $bytes))
                $record.legacyHex[$variantId] = (($bytes | ForEach-Object { '{0:X2}' -f $_ }) -join '')
            }
        }
        $aboutUtf8[$variantId] = [System.Collections.Generic.List[string]]::new()
        foreach ($record in $entriesByRole.About) {
            $bytes = [System.Text.UTF8Encoding]::new($false, $true).GetBytes(
                [string]$record.texts[$variantId])
            Assert-ByteLimit -Bytes $bytes -Limit 255 -Target "UTF-8/$variantId" -Id $record.id
            $aboutUtf8[$variantId].Add((Convert-ToByteLiteral -Bytes $bytes))
            $record.utf8Hex[$variantId] = (($bytes | ForEach-Object { '{0:X2}' -f $_ }) -join '')
        }
        $errorUtf8[$variantId] = [System.Collections.Generic.List[string]]::new()
        foreach ($record in $entriesByRole.Error) {
            $bytes = [System.Text.UTF8Encoding]::new($false, $true).GetBytes(
                [string]$record.texts[$variantId])
            Assert-ByteLimit -Bytes $bytes -Limit 255 -Target "UTF-8/$variantId" -Id $record.id
            $errorUtf8[$variantId].Add((Convert-ToByteLiteral -Bytes $bytes))
            $record.utf8Hex[$variantId] = (($bytes | ForEach-Object { '{0:X2}' -f $_ }) -join '')
        }
    }

    $detailKeys = [System.Collections.Generic.List[string]]::new()
    foreach ($role in $roles) {
        $roleEntries = @($entriesByRole[$role])
        for ($index = 0; $index -lt $roleEntries.Count; $index++) {
            $detailKeys.Add(
                "inline constexpr AeText::TextToken k${role}_$($roleEntries[$index].id) = { AeText::TextRole::$role, $index };")
        }
    }

    $stringTables = [System.Collections.Generic.List[string]]::new()
    $symbols = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($variant in $generatedVariants) {
        $variantId = [string]$variant.id
        $symbol = Get-VariantSymbol -Id $variantId
        if (-not $symbols.Add($symbol)) {
            throw "Family Variant IDs collide as C++ symbols: $variantId"
        }
        foreach ($role in $roles) {
            $table = New-StringTable -Name (Get-ArrayName -Role $role -Variant $symbol) `
                -Literals @($encoded[$variantId][$role])
            if ($null -ne $table) {
                $stringTables.Add($table)
            }
        }
        foreach ($table in @(
            (New-StringTable -Name "kAboutUtf8$symbol" -Literals @($aboutUtf8[$variantId])),
            (New-StringTable -Name "kErrorUtf8$symbol" -Literals @($errorUtf8[$variantId])))) {
            if ($null -ne $table) {
                $stringTables.Add($table)
            }
        }
    }

    $variantBlocks = [System.Collections.Generic.List[string]]::new()
    $variantEntries = [System.Collections.Generic.List[string]]::new()
    $fallbackIndex = -1
    for ($variantIndex = 0; $variantIndex -lt $generatedVariants.Count; $variantIndex++) {
        $variant = $generatedVariants[$variantIndex]
        $variantId = [string]$variant.id
        $symbol = Get-VariantSymbol -Id $variantId
        if ($variantId -ceq $resolvedDefaultVariantId) {
            $fallbackIndex = $variantIndex
        }
        $roleTables = [System.Collections.Generic.List[string]]::new()
        foreach ($role in $roles) {
            $roleTables.Add("    $(Get-TableInitializer -Name (Get-ArrayName -Role $role -Variant $symbol) -Count $entriesByRole[$role].Count),")
        }
        $variantBlocks.Add((Expand-GeneratorTemplate -Name 'EffectVariant.h.template' -Values @{
            SYMBOL = $symbol
            ROLE_TABLES = $roleTables -join "`n"
            ID_LITERAL = Convert-ToCppNarrowLiteral -Value $variantId
            ABOUT_UTF8 = Get-TableInitializer -Name "kAboutUtf8$symbol" -Count $entriesByRole.About.Count
            ERROR_UTF8 = Get-TableInitializer -Name "kErrorUtf8$symbol" -Count $entriesByRole.Error.Count
        }))
        $variantEntries.Add("    k${symbol}Variant,")
    }

    $accessors = [System.Collections.Generic.List[string]]::new()
    foreach ($role in $roles) {
        if ($entriesByRole[$role].Count -eq 0) {
            continue
        }
        $resolver = if ($role -in @('Param', 'Label', 'Popup', 'Topic')) {
            'Static'
        } elseif ($role -eq 'About') {
            'About'
        } else {
            'Error'
        }
        $returnType = if ($role -eq 'About') {
            'AeText::AboutText'
        } else {
            'const char *'
        }
        $accessors.Add((Expand-GeneratorTemplate -Name 'EffectSourceAccessor.h.template' -Values @{
            RETURN_TYPE = $returnType
            METHOD = $role
            RESOLVER = $resolver
        }))
    }

    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($role in $roles) {
        foreach ($prefix in @('AETEXT_', 'AETEXT_VERBATIM_')) {
            $name = "$prefix$($role.ToUpperInvariant())"
            $lines.Add("#ifdef $name")
            $lines.Add("#undef $name")
            $lines.Add('#endif')
                $lines.Add("#define $name(strings, stable_id) \")
            $lines.Add("    (strings).$role(::$Namespace`::detail::k${role}_##stable_id)")
        }
    }
    $wrapperMacros = $lines -join "`n"

    $runtimeIdentityBlock = if ($SingleLanguage) {
        ''
    } else {
        @(
            "inline constexpr char kRuntimeSuiteName[] = $(Convert-ToCppNarrowLiteral -Value ([string]$RuntimeIdentity.suite.name));"
            "inline constexpr std::int32_t kRuntimeSuiteVersion = $([string]$RuntimeIdentity.suite.version);"
        ) -join "`n"
    }
    $clientArguments = if ($SingleLanguage) {
        @(
            '            in_data,'
            '            Catalog(),'
            '            nullptr,'
            '            0'
        ) -join "`n"
    } else {
        @(
            '            in_data,'
            '            Catalog(),'
            '            detail::kRuntimeSuiteName,'
            '            detail::kRuntimeSuiteVersion'
        ) -join "`n"
    }
    $openSettingsBody = if ($SingleLanguage) {
        @(
            '    (void)in_data;'
            '    (void)title;'
        ) -join "`n"
    } else {
        @(
            '    AeText::Client client('
            '        in_data,'
            '        Catalog(),'
            '        detail::kRuntimeSuiteName,'
            '        detail::kRuntimeSuiteVersion);'
            '    client.OpenSettings(title);'
        ) -join "`n"
    }

    $header = Expand-GeneratorTemplate -Name 'EffectHeader.h.template' -Values @{
        NAMESPACE = $Namespace
        RUNTIME_IDENTITY = $runtimeIdentityBlock
        DETAIL_KEYS = $detailKeys -join "`n"
        STRING_TABLES = $stringTables -join "`n`n"
        VARIANT_BLOCKS = $variantBlocks -join "`n`n"
        VARIANT_ENTRIES = $variantEntries -join "`n"
        FALLBACK_INDEX = [string]$fallbackIndex
        ACCESSORS = $accessors -join "`n`n"
        CLIENT_ARGUMENTS = $clientArguments
        OPEN_SETTINGS_BODY = $openSettingsBody
        WRAPPER_MACROS = $wrapperMacros
    }
    $roleCounts = [ordered]@{}
    $byteEntries = [System.Collections.Generic.List[object]]::new()
    foreach ($role in $roles) {
        $roleCounts[$role] = $entriesByRole[$role].Count
        foreach ($record in $entriesByRole[$role]) {
            $entry = [ordered]@{
                role = $role
                stableId = $record.id
                legacyHex = $record.legacyHex
            }
            if ($role -in @('About', 'Error')) {
                $entry.utf8Hex = $record.utf8Hex
            }
            $byteEntries.Add([pscustomobject]$entry)
        }
    }
    $byteReport = [ordered]@{
        schemaVersion = 1
        variants = @($generatedVariants | ForEach-Object { [string]$_.id })
        bindings = [ordered]@{
            uniqueCount = $byteEntries.Count
            roleCounts = $roleCounts
            entries = @($byteEntries)
        }
    }
    return [pscustomobject]@{
        HeaderLines = @($header -split "`n")
        ByteReport = $byteReport
    }
}
