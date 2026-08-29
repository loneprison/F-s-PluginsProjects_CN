function Write-SettingsHeader {
    param(
        [Parameter(Mandatory = $true)][object]$Root,
        [Parameter(Mandatory = $true)][object]$RuntimeIdentity
    )

    Assert-Properties -Value $Root -Allowed @('entries', 'references') -Name 'catalog'
    if ($Root.entries -isnot [object[]] -or $Root.entries.Count -eq 0) {
        throw 'catalog.entries must be a non-empty array.'
    }
    if ($Root.references -isnot [object[]] -or $Root.references.Count -eq 0) {
        throw 'catalog.references must be a non-empty array.'
    }

    $entries = [System.Collections.Generic.List[object]]::new()
    $entriesById = [ordered]@{}
    $tokens = @{}
    foreach ($entry in @($Root.entries)) {
        Assert-Object -Value $entry -Name 'settings entry'
        Assert-Properties -Value $entry -Allowed @('id', 'token', 'en', 'zh', 'ja') -Name 'settings entry'
        $id = Get-RequiredString -Value $entry -Property 'id' -Name 'settings entry'
        $token = Get-RequiredString -Value $entry -Property 'token' -Name "settings entry $id"
        $chinese = Get-RequiredString -Value $entry -Property 'zh' -Name "settings entry $id"
        if ($id -cnotmatch '^L10N_[A-Z0-9]+(?:_[A-Z0-9]+)*$') {
            throw "Invalid stable text id: $id"
        }
        if ($token -cnotmatch '^[A-Z][A-Za-z0-9]*$') {
            throw "Invalid C++ token: id=$id token=$token"
        }
        if ($entriesById.Contains($id)) {
            throw "Duplicate stable text id: $id"
        }
        if ($tokens.ContainsKey($token)) {
            throw "Duplicate settings C++ token: $token"
        }
        $englishProperty = $entry.PSObject.Properties['en']
        $japaneseProperty = $entry.PSObject.Properties['ja']
        $english = Get-OptionalString -Value $entry -Property 'en' -Fallback $chinese -Language 'en' -Id $id
        $japanese = Get-OptionalString -Value $entry -Property 'ja' -Fallback $chinese -Language 'ja' -Id $id
        Assert-Placeholders -Id $id -Language 'en' -Original $chinese -Translation $english
        Assert-Placeholders -Id $id -Language 'ja' -Original $chinese -Translation $japanese
        $record = [pscustomobject]@{
            id = $id
            token = $token
            en = $english
            zh = $chinese
            ja = $japanese
            en_explicit = $null -ne $englishProperty -and $englishProperty.Value -is [string] -and $englishProperty.Value.Length -gt 0
            ja_explicit = $null -ne $japaneseProperty -and $japaneseProperty.Value -is [string] -and $japaneseProperty.Value.Length -gt 0
        }
        $entries.Add($record)
        $entriesById[$id] = $record
        $tokens[$token] = $true
    }

    $referencedIds = @{}
    foreach ($reference in @($Root.references)) {
        if ($reference -isnot [string] -or $reference.Length -eq 0) {
            throw 'Each settings reference must be a non-empty stable id string.'
        }
        if ($referencedIds.ContainsKey($reference)) {
            throw "Duplicate settings reference: $reference"
        }
        if (-not $entriesById.Contains($reference)) {
            throw "Settings reference has no catalog entry: $reference"
        }
        $referencedIds[$reference] = $true
    }
    foreach ($id in $entriesById.Keys) {
        if (-not $referencedIds.ContainsKey($id)) {
            throw "Unused settings catalog entry: $id"
        }
    }

    $enumEntries = [System.Collections.Generic.List[string]]::new()
    for ($index = 0; $index -lt $entries.Count; $index++) {
        $enumEntries.Add("    $($entries[$index].token) = $index, // $($entries[$index].id)")
    }

    $languageTables = [System.Collections.Generic.List[string]]::new()
    foreach ($language in @('English', 'SimplifiedChinese', 'Japanese')) {
        $literals = [System.Collections.Generic.List[string]]::new()
        foreach ($entry in $entries) {
            $value = switch ($language) {
                'English' { $entry.en }
                'SimplifiedChinese' { $entry.zh }
                'Japanese' { $entry.ja }
            }
            $literals.Add("    $(Convert-ToWideLiteral -Value $value),")
        }
        $languageTables.Add((Expand-GeneratorTemplate -Name 'WideStringTable.h.template' -Values @{
            NAME = "k$language"
            LITERALS = ($literals -join "`n")
        }))
    }

    $header = Expand-GeneratorTemplate -Name 'SettingsHeader.h.template' -Values @{
        NAMESPACE = $Namespace
        ENUM_ENTRIES = ($enumEntries -join "`n")
        LANGUAGE_TABLES = ($languageTables -join "`n`n")
        TEXT_COUNT = $entries.Count
        SUITE_NAME = Convert-ToCppNarrowLiteral -Value ([string]$RuntimeIdentity.suite.name)
        SUITE_VERSION = [string]$RuntimeIdentity.suite.version
        SUITE_INTERNAL_VERSION = [string]$RuntimeIdentity.suite.internalVersion
        CONFIG_DIRECTORY = Convert-ToWideLiteral -Value ([string]$RuntimeIdentity.config.directoryName)
        CONFIG_FILE = Convert-ToWideLiteral -Value ([string]$RuntimeIdentity.config.fileName)
        CONFIG_BACKUP_FILE = Convert-ToWideLiteral -Value ([string]$RuntimeIdentity.config.invalidBackupFileName)
        CONFIG_MUTEX = Convert-ToWideLiteral -Value ([string]$RuntimeIdentity.config.mutexName)
    }
    return [pscustomobject]@{ HeaderLines = @($header -split "`n") }
}
