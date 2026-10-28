# Sets the cron dispatch token (zeynmedia-only) and the NVIDIA NIM key. Values are typed here, never stored in files.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot)

Write-Host "`n=== 1/2  Zamanlayici token'i (sadece zeynmedia) ===" -ForegroundColor Cyan
Write-Host "Tarayicida token sayfasi acildi: ayarlar dolu, en altta 'Generate token' bas, cikan token'i kopyala."
Start-Process 'https://github.com/settings/personal-access-tokens/new?name=zeynmedia-cron&description=Hourly+Shorts+dispatch&target_name=zeynmedia&expires_in=none&actions=write'
$t = Read-Host "Token'i yapistir (github_pat_...) ve Enter"
if ($t.Trim()) {
	$t.Trim() | npx --prefix ..\zeynmedia-studio wrangler secret put GH_DISPATCH_TOKEN --config cron\wrangler.jsonc
}

Write-Host "`n=== 2/2  NVIDIA NIM API key ===" -ForegroundColor Cyan
$k = Read-Host "NVIDIA key'i yapistir (nvapi-...) ve Enter"
if ($k.Trim()) {
	foreach ($r in 'zeynmedia-shorts-factory', 'zeynmedia-studio') {
		$k.Trim() | gh secret set NVIDIA_API_KEY -R "zeynmedia/$r"
	}
}
Write-Host "`nTamam, pencereyi kapatabilirsin." -ForegroundColor Green
