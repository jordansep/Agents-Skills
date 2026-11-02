<#
.SYNOPSIS
  Instala los skills de los agentes desde una copia aislada del repositorio, fija en origin/main.

.DESCRIPTION
  Los skills que usan las sesiones de otros repositorios no deben salir de la carpeta de trabajo
  de este repositorio: si salieran de ahí, ejecutarían la rama que esté abierta y escribirían en ella.

  Este script:
    1. Crea (o actualiza) un git worktree en -Destino, desacoplado (detached) en origin/main.
       Si esa copia tiene cambios locales, se detiene y los muestra: nadie debería escribir ahí.
    2. Enlaza cada skill de los agentes (agentes/*/agente.json) en -Skills con una junction
       a esa copia. Solo reemplaza junctions o enlaces; si encuentra una carpeta real, se detiene.

  Para actualizar los skills instalados después de un merge, vuelve a ejecutarlo.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\instalar_skills.ps1
#>
param(
  [string]$Destino = (Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) "Agents-Skills-instalado"),
  [string]$Skills = (Join-Path $env:USERPROFILE ".claude\skills"),
  [string]$Rama = "origin/main"
)
$ErrorActionPreference = "Stop"
$repo = Split-Path $PSScriptRoot -Parent

function Git { & git -C $repo @args; if ($LASTEXITCODE) { throw "git $args falló" } }

Git fetch --quiet origin

# 1. Copia aislada
if (-not (Test-Path $Destino)) {
  Git worktree add --detach $Destino $Rama
} else {
  $cambios = & git -C $Destino status --porcelain
  if ($cambios) {
    Write-Host "La copia instalada ($Destino) tiene cambios locales. Alguien escribió en ella:" -ForegroundColor Red
    $cambios | ForEach-Object { Write-Host "  $_" }
    Write-Host "Revisalos (y llevalos a un PR si corresponde) antes de reinstalar. No se tocó nada." -ForegroundColor Red
    exit 1
  }
  & git -C $Destino checkout --quiet --detach $Rama
  if ($LASTEXITCODE) { throw "no se pudo actualizar $Destino" }
}
$commit = & git -C $Destino log -1 --format="%h %s"
Write-Host "Copia instalada: $Destino ($commit)"

# 2. Enlaces de los skills
New-Item -ItemType Directory -Force $Skills | Out-Null
$nombres = Get-ChildItem (Join-Path $Destino "agentes") -Filter agente.json -Recurse |
  ForEach-Object { (Get-Content $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json).skills } |
  ForEach-Object { Split-Path $_ -Leaf }

foreach ($n in $nombres) {
  $enlace = Join-Path $Skills $n
  $objetivo = Join-Path $Destino "skills\$n"
  $item = Get-Item $enlace -Force -ErrorAction SilentlyContinue
  if ($item) {
    if (-not $item.LinkType) {
      Write-Host "$enlace es una carpeta real, no un enlace. No la borro: movela o borrala vos y volvé a ejecutar." -ForegroundColor Red
      exit 1
    }
    $item.Delete()  # borra solo el enlace, no el contenido
  }
  New-Item -ItemType Junction -Path $enlace -Target $objetivo | Out-Null
  Write-Host "  $n -> $objetivo"
}
Write-Host "Listo. Los skills instalados ya no dependen de la rama abierta en $repo."
