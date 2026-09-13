function Get-CodePointSegments {
    param([Parameter(Mandatory = $true)][string]$Value)

    $segments = [System.Collections.Generic.List[object]]::new()
    for ($index = 0; $index -lt $Value.Length; $index++) {
        $first = [char]$Value[$index]
        if ([char]::IsHighSurrogate($first)) {
            if ($index + 1 -ge $Value.Length -or -not [char]::IsLowSurrogate([char]$Value[$index + 1])) {
                throw 'Text contains an unmatched UTF-16 high surrogate.'
            }
            $second = [char]$Value[++$index]
            $segments.Add([pscustomobject]@{
                Text = [string]::Concat($first, $second)
                CodePoint = [char]::ConvertToUtf32($first, $second)
            })
            continue
        }
        if ([char]::IsLowSurrogate($first)) {
            throw 'Text contains an unmatched UTF-16 low surrogate.'
        }
        $segments.Add([pscustomobject]@{
            Text = [string]$first
            CodePoint = [int]$first
        })
    }
    return $segments
}

function Get-StrictEncoding {
    param([Parameter(Mandatory = $true)][int]$CodePage)

    return [System.Text.Encoding]::GetEncoding(
        $CodePage,
        [System.Text.EncoderExceptionFallback]::new(),
        [System.Text.DecoderExceptionFallback]::new())
}

function Convert-ToTargetBytes {
    param(
        [Parameter(Mandatory = $true)][string]$Value,
        [Parameter(Mandatory = $true)][System.Text.Encoding]$Encoding,
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $true)][string]$Id,
        [switch]$AeDisplayProfile
    )

    $bytes = [System.Collections.Generic.List[byte]]::new()
    foreach ($segment in @(Get-CodePointSegments -Value $Value)) {
        if ($AeDisplayProfile -and $segment.CodePoint -eq 0x30FB) {
            $bytes.Add(0xA1)
            $bytes.Add(0xA4)
            continue
        }
        try {
            $encoded = $Encoding.GetBytes([string]$segment.Text)
            foreach ($byte in $encoded) {
                $bytes.Add($byte)
            }
        } catch {
            Add-Issue ('Unmapped character: target={0} id={1} codepoint=U+{2:X4}' -f $Target, $Id, $segment.CodePoint)
            $bytes.Add(0x3F)
        }
    }
    return $bytes.ToArray()
}

function Convert-ToByteLiteral {
    param([Parameter(Mandatory = $true)][byte[]]$Bytes)

    if ($Bytes.Count -eq 0) {
        return '""'
    }
    return '"' + (($Bytes | ForEach-Object { '\x{0:X2}' -f $_ }) -join '') + '"'
}

function Convert-ToWideLiteral {
    param([Parameter(Mandatory = $true)][string]$Value)

    $builder = [System.Text.StringBuilder]::new()
    [void]$builder.Append('L"')
    foreach ($segment in @(Get-CodePointSegments -Value $Value)) {
        $code = [int]$segment.CodePoint
        if ($code -eq 9) {
            [void]$builder.Append('\t')
        } elseif ($code -eq 10) {
            [void]$builder.Append('\n')
        } elseif ($code -eq 13) {
            [void]$builder.Append('\r')
        } elseif ($code -eq 34) {
            [void]$builder.Append('\"')
        } elseif ($code -eq 92) {
            [void]$builder.Append('\\')
        } elseif ($code -ge 0x20 -and $code -le 0x7E) {
            [void]$builder.Append([string]$segment.Text)
        } elseif ($code -le 0xFFFF) {
            [void]$builder.AppendFormat('\u{0:X4}', $code)
        } else {
            [void]$builder.AppendFormat('\U{0:X8}', $code)
        }
    }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function Assert-ByteLimit {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Bytes,
        [Parameter(Mandatory = $true)][int]$Limit,
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $true)][string]$Id
    )

    if ($Bytes.Count -gt $Limit) {
        throw "Text exceeds $Limit-byte limit: target=$Target id=$Id bytes=$($Bytes.Count)"
    }
}

function Test-CanEncode {
    param(
        [Parameter(Mandatory = $true)][string]$Value,
        [Parameter(Mandatory = $true)][System.Text.Encoding]$Encoding
    )

    try {
        [void]$Encoding.GetBytes($Value)
        return $true
    } catch {
        return $false
    }
}
