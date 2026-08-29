function Test-ByteArraysEqual {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Left,
        [Parameter(Mandatory = $true)][byte[]]$Right
    )

    if ($Left.Count -ne $Right.Count) {
        return $false
    }
    for ($index = 0; $index -lt $Left.Count; $index++) {
        if ($Left[$index] -ne $Right[$index]) {
            return $false
        }
    }
    return $true
}

function Convert-ToUtf8BomBytes {
    param([Parameter(Mandatory = $true)][object]$Lines)

    $contents = (@($Lines) -join "`r`n") + "`r`n"
    $preamble = [byte[]](0xEF, 0xBB, 0xBF)
    $body = [System.Text.UTF8Encoding]::new($false).GetBytes($contents)
    $bytes = [byte[]]::new($preamble.Count + $body.Count)
    [System.Array]::Copy($preamble, 0, $bytes, 0, $preamble.Count)
    [System.Array]::Copy($body, 0, $bytes, $preamble.Count, $body.Count)
    return $bytes
}

function Write-AtomicBytesIfChanged {
    param(
        [Parameter(Mandatory = $true)][string]$ResolvedPath,
        [Parameter(Mandatory = $true)][string]$TemporaryPath,
        [Parameter(Mandatory = $true)][byte[]]$Bytes
    )

    if ([System.IO.File]::Exists($ResolvedPath)) {
        $oldBytes = [System.IO.File]::ReadAllBytes($ResolvedPath)
        if (Test-ByteArraysEqual -Left $oldBytes -Right $Bytes) {
            return
        }
    }

    $directory = [System.IO.Path]::GetDirectoryName($ResolvedPath)
    [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    [System.IO.File]::WriteAllBytes($TemporaryPath, $Bytes)
    if ([System.IO.File]::Exists($ResolvedPath)) {
        $backupPath = "$ResolvedPath.bak.$PID.$([Guid]::NewGuid().ToString('N'))"
        try {
            [System.IO.File]::Replace($TemporaryPath, $ResolvedPath, $backupPath)
        } finally {
            if ([System.IO.File]::Exists($backupPath)) {
                [System.IO.File]::Delete($backupPath)
            }
        }
    } else {
        [System.IO.File]::Move($TemporaryPath, $ResolvedPath)
    }
}
