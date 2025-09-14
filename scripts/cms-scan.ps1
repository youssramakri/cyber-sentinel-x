<#
.SYNOPSIS
Script pour lancer rapidement le CMS scanner depuis PowerShell.
.EXAMPLE
.\cms-scan.ps1 -url "https://www.bbcamerica.com"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$url,
    
    [string]$endpoint = "http://localhost:5000/api/scan/cms"
)

# Préparer le JSON
$body = @{ url = $url } | ConvertTo-Json

try {
    # Appel API CMS Scanner
    $response = Invoke-RestMethod -Uri $endpoint -Method Post -Body $body -ContentType "application/json"
    # Afficher le résultat formaté
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Error "Erreur lors de l'appel au CMS scanner : $($_.Exception.Message)"
}
