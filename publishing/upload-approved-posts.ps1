param(
  [Parameter(Mandatory=$true)][string]$SourceFolder
)
$ErrorActionPreference = "Stop"
$repo = "https://github.com/MarufTahmid013/ainversia-social-media.git"
$work = Join-Path $env:TEMP "ainversia-social-media-upload"
if (-not (Test-Path $SourceFolder -PathType Container)) { throw "Folder not found: $SourceFolder" }
$names = 1..4 | ForEach-Object { "ainversia_post_$_.png" }
foreach ($name in $names) {
  if (-not (Test-Path (Join-Path $SourceFolder $name) -PathType Leaf)) { throw "Missing image: $name" }
}
git --version | Out-Null
if (Test-Path (Join-Path $work ".git")) {
  git -C $work pull --ff-only
  if ($LASTEXITCODE -ne 0) { throw "Git pull failed" }
} else {
  if (Test-Path $work) { throw "Upload directory exists but is not a Git repository: $work" }
  git clone $repo $work
  if ($LASTEXITCODE -ne 0) { throw "Git clone failed" }
}
$dest = Join-Path $work "media\posts"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($name in $names) { Copy-Item -LiteralPath (Join-Path $SourceFolder $name) -Destination (Join-Path $dest $name) -Force }
git -C $work add -- media/posts
if ($LASTEXITCODE -ne 0) { throw "Git add failed" }
git -C $work diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Write-Host "Images already uploaded; nothing to commit." }
else {
  git -C $work commit -m "Upload four approved AinVersia social graphics"
  if ($LASTEXITCODE -ne 0) { throw "Git commit failed. Configure Git name/email if prompted." }
  git -C $work push origin HEAD:main
  if ($LASTEXITCODE -ne 0) { throw "Git push failed. Check GitHub authentication." }
}
Write-Host "Done. Public image URLs:"
foreach ($name in $names) { Write-Host "https://raw.githubusercontent.com/MarufTahmid013/ainversia-social-media/main/media/posts/$name" }
