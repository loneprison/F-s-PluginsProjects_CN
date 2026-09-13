$script:AeTextGeneratorTemplateDirectory = Join-Path $PSScriptRoot 'templates'

function Expand-GeneratorTemplate {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][hashtable]$Values
    )

    $path = Join-Path $script:AeTextGeneratorTemplateDirectory $Name
    $contents = [System.IO.File]::ReadAllText($path).Replace("`r`n", "`n").TrimEnd("`r", "`n")
    foreach ($entry in $Values.GetEnumerator()) {
        $contents = $contents.Replace("{{$($entry.Key)}}", [string]$entry.Value)
    }
    return $contents
}
