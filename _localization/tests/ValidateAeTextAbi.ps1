$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$publicHeader = Join-Path $root '_localization\AeText.h'
if (-not (Test-Path -LiteralPath $publicHeader -PathType Leaf)) {
    throw 'red phase: _localization\AeText.h is not implemented.'
}

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere)) {
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

$devCommand = Join-Path $installation 'Common7\Tools\VsDevCmd.bat'
$headers = Join-Path (Split-Path -Parent $root) 'Headers'
$scratch = Join-Path ([System.IO.Path]::GetTempPath()) (
    'AeTextAbiTests-' + [Guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($scratch) | Out-Null

try {
    $commandPath = Join-Path $scratch 'build.cmd'
    $executable = Join-Path $scratch 'ValidateAeTextAbi.exe'
    $testObject = Join-Path $scratch 'ValidateAeTextAbi.obj'
    $compileOptions = '/nologo /std:c++20 /EHsc /W4 /WX /utf-8 /Zp16 /DMSWindows /DWIN32 /D_WINDOWS'
    $includeOptions = '/I"{0}" /I"{1}" /I"{2}" /I"{3}"' -f `
        (Join-Path $root '_localization'), `
        $headers, `
        (Join-Path $headers 'SP'), `
        (Join-Path $headers 'Win')
    $commands = @(
        '@echo off',
        ('call "{0}" -no_logo -arch=x64 -host_arch=x64' -f $devCommand),
        'if errorlevel 1 exit /b %errorlevel%',
        ('cl.exe {0} {1} /c "{2}" /Fo:"{3}"' -f `
            $compileOptions, $includeOptions, `
            (Join-Path $PSScriptRoot 'ValidateAeTextAbi.cpp'), $testObject),
        'if errorlevel 1 exit /b %errorlevel%',
        ('cl.exe /nologo "{0}" /Fe:"{1}" /link /INCREMENTAL:NO' -f `
            $testObject, $executable)
    )
    [System.IO.File]::WriteAllLines(
        $commandPath, $commands, [System.Text.Encoding]::ASCII)

    & cmd.exe /d /c $commandPath
    if ($LASTEXITCODE -ne 0) {
        throw "AeText ABI contract test compilation failed with exit code $LASTEXITCODE."
    }

    & $executable
    if ($LASTEXITCODE -ne 0) {
        throw "AeText ABI contract validation failed with exit code $LASTEXITCODE."
    }
} finally {
    if (Test-Path -LiteralPath $scratch) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
