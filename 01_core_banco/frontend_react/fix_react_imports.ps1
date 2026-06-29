$srcPath = "src"

if (!(Test-Path $srcPath)) {
    Write-Host "No se encontró la carpeta src"
    exit 1
}

$files = Get-ChildItem -Path $srcPath -Recurse -Include *.jsx,*.js

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw

    $usesJsx = $content -match "<[A-Za-z]" -or $content -match "<>"
    $hasReactDefault = $content -match "import\s+React\b" -or $content -match "import\s+\*\s+as\s+React"

    if ($usesJsx -and -not $hasReactDefault) {
        $newContent = "import React from `"react`";`r`n" + $content
        Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8
        Write-Host "Corregido:" $file.FullName
    }
}

Write-Host "Revisión completada."
