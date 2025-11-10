# Iniciar Dashboard Multi-Deporte
# Script de inicio rapido

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DASHBOARD MULTI-DEPORTE" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Iniciando dashboard..." -ForegroundColor Green
Write-Host ""

# Activar entorno virtual si existe
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "OK - Activando entorno virtual..." -ForegroundColor Green
    & .\.venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "Lanzando Streamlit..." -ForegroundColor Cyan
Write-Host ""
Write-Host "El dashboard se abrira en:" -ForegroundColor Yellow
Write-Host "   >> http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "TIPS:" -ForegroundColor Cyan
Write-Host "   - Presiona Ctrl+C para detener" -ForegroundColor Gray
Write-Host "   - Acceso desde movil: usa Network URL" -ForegroundColor Gray
Write-Host "   - Presiona 'C' en el dashboard para limpiar cache" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar streamlit
python -m streamlit run src/dashboard/multi_sport_app.py
