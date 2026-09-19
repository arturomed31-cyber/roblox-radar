$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$games = [System.IO.File]::ReadAllText("$PWD\raw_v3.json",[System.Text.Encoding]::UTF8) | ConvertFrom-Json
$games = @($games | Sort-Object -Property playing -Descending)
$n = $games.Count

$CELL = 96
$COLS = 29
$ROWS = [Math]::Ceiling($n / $COLS)
$sprite = New-Object System.Drawing.Bitmap ($COLS * $CELL), ($ROWS * $CELL)
$gfx = [System.Drawing.Graphics]::FromImage($sprite)
$gfx.Clear([System.Drawing.Color]::FromArgb(255, 32, 36, 46))
$gfx.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$gfx.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality

$wc = New-Object System.Net.WebClient
$wc.Headers.Add("User-Agent", "Mozilla/5.0")

$map = @{}
$ok = 0
for ($i = 0; $i -lt $n; $i++) {
    $g = $games[$i]
    $col = $i % $COLS; $row = [Math]::Floor($i / $COLS)
    $map[[string]$g.id] = @($col, $row)
    if (-not $g.icon) { continue }
    try {
        $bytes = $wc.DownloadData($g.icon)
        $ms = New-Object System.IO.MemoryStream (,$bytes)
        $img = [System.Drawing.Image]::FromStream($ms)
        $gfx.DrawImage($img, ($col * $CELL), ($row * $CELL), $CELL, $CELL)
        $img.Dispose(); $ms.Dispose()
        $ok++
    } catch { }
    if ($i % 100 -eq 0) { Write-Output "  icons $i/$n (ok $ok)" }
}
$gfx.Dispose()

$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality, [long]84)
$sprite.Save("$PWD\icons.jpg", $enc, $ep)
$sprite.Dispose()
Write-Output "sprite saved: $((Get-Item icons.jpg).Length) bytes, icons ok: $ok / $n, grid ${COLS}x${ROWS}"

# ---- thumbnails for the top games ----
$TOP = 240
if (-not (Test-Path "$PWD\thumbs")) { New-Item -ItemType Directory -Path "$PWD\thumbs" | Out-Null }
$thumbIds = @()
$ep2 = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep2.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality, [long]78)
for ($i = 0; $i -lt [Math]::Min($TOP, $n); $i++) {
    $g = $games[$i]
    if (-not $g.thumb) { continue }
    try {
        $bytes = $wc.DownloadData($g.thumb)
        $ms = New-Object System.IO.MemoryStream (,$bytes)
        $img = [System.Drawing.Image]::FromStream($ms)
        $bmp = New-Object System.Drawing.Bitmap 480, 270
        $g2 = [System.Drawing.Graphics]::FromImage($bmp)
        $g2.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g2.DrawImage($img, 0, 0, 480, 270)
        $g2.Dispose()
        $bmp.Save("$PWD\thumbs\$($g.id).jpg", $enc, $ep2)
        $bmp.Dispose(); $img.Dispose(); $ms.Dispose()
        $thumbIds += [string]$g.id
    } catch { }
}
Write-Output "thumbs saved: $($thumbIds.Count)"

$meta = [PSCustomObject]@{ cell = $CELL; cols = $COLS; rows = $ROWS; map = $map; thumbs = $thumbIds }
$json = $meta | ConvertTo-Json -Depth 4 -Compress
[System.IO.File]::WriteAllText("$PWD\images_meta.json", $json, [System.Text.UTF8Encoding]::new($false))
Write-Output "images_meta.json written"
