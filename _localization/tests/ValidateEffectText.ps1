$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
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
$scratch = Join-Path ([System.IO.Path]::GetTempPath()) ("FsEffectTextTests-" + [Guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($scratch) | Out-Null

$effectInputs = @(
    (Join-Path $root '_localization\AeText.h'),
    (Join-Path $root '_localization\core\AeTextClient.cpp'),
    (Join-Path $root '_localization\families\fs\FsAeText.targets'),
    (Join-Path $root '_localization\generator\templates\EffectHeader.h.template')
)
$forbiddenEffectDependencies = 'language\.json|HostEnvironment|ResolveAutomatic|LanguageConfig'
foreach ($inputPath in $effectInputs) {
    $match = Select-String -LiteralPath $inputPath -Pattern $forbiddenEffectDependencies
    if ($match) {
        throw "Effect-side source-only fallback depends on Runtime-owned language policy: $($match.Path):$($match.LineNumber)"
    }
}

try {
    $commandPath = Join-Path $scratch 'build.cmd'
    $executable = Join-Path $scratch 'ValidateEffectText.exe'
    $effectObject = Join-Path $scratch 'AeTextClient.obj'
    $testObject = Join-Path $scratch 'ValidateEffectText.obj'
    $compileOptions = '/nologo /std:c++20 /EHsc /W4 /WX /utf-8 /DMSWindows /DWIN32 /D_WINDOWS'
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
            $compileOptions, $includeOptions, (Join-Path $root '_localization\core\AeTextClient.cpp'), $effectObject),
        'if errorlevel 1 exit /b %errorlevel%',
        ('cl.exe {0} {1} /c "{2}" /Fo:"{3}"' -f `
            $compileOptions, $includeOptions, (Join-Path $PSScriptRoot 'ValidateEffectText.cpp'), $testObject),
        'if errorlevel 1 exit /b %errorlevel%',
        ('cl.exe /nologo "{0}" "{1}" /Fe:"{2}" /link /INCREMENTAL:NO' -f `
            $effectObject, $testObject, $executable)
    )
    [System.IO.File]::WriteAllLines($commandPath, $commands, [System.Text.Encoding]::ASCII)

    & cmd.exe /d /c $commandPath
    if ($LASTEXITCODE -ne 0) {
        throw "EffectText contract test compilation failed with exit code $LASTEXITCODE."
    }

    & $executable
    if ($LASTEXITCODE -ne 0) {
        throw "EffectText contract validation failed with exit code $LASTEXITCODE."
    }
} finally {
    if (Test-Path -LiteralPath $scratch) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
