$script:FsTextGeneratorTemplateDirectory = Join-Path $PSScriptRoot 'templates'

function Expand-GeneratorTemplate {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][hashtable]$Values
    )

    $path = Join-Path $script:FsTextGeneratorTemplateDirectory $Name
    $contents = [System.IO.File]::ReadAllText($path).Replace("`r`n", "`n").TrimEnd("`r", "`n")
    foreach ($entry in $Values.GetEnumerator()) {
        $contents = $contents.Replace("{{$($entry.Key)}}", [string]$entry.Value)
    }
    $unresolved = [regex]::Match($contents, '\{\{[A-Z0-9_]+\}\}')
    if ($unresolved.Success) {
        throw "Unresolved generator template placeholder: template=$Name placeholder=$($unresolved.Value)"
    }
    return $contents
}
