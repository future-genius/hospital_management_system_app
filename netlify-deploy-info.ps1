#!/usr/bin/env powershell
# Netlify Deployment Setup Script
# This script helps you prepare your app for Netlify deployment

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Hospital Management System" -ForegroundColor Cyan
Write-Host "Netlify Deployment Helper" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is available
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "✅ Git is installed" -ForegroundColor Green
} else {
    Write-Host "❌ Git is not installed" -ForegroundColor Red
    exit 1
}

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python is not installed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Files Ready for Deployment:" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$deploymentFiles = @(
    "netlify.toml",
    "netlify/functions/app.py",
    "runtime.txt",
    ".env.example",
    ".gitignore"
)

foreach ($file in $deploymentFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file MISSING" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Ready to Deploy" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Step 1: Commit and push to GitHub:" -ForegroundColor Yellow
Write-Host "  git add ." -ForegroundColor White
Write-Host "  git commit -m 'Netlify deployment configuration'" -ForegroundColor White
Write-Host "  git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "Step 2: Visit https://netlify.com" -ForegroundColor Yellow
Write-Host "Step 3: Connect your GitHub repository" -ForegroundColor Yellow
Write-Host "Step 4: Set environment variables in Netlify Dashboard" -ForegroundColor Yellow
Write-Host "  - SECRET_KEY: <generate secure key>" -ForegroundColor White
Write-Host "  - DATABASE_URL: <postgres url or leave empty>" -ForegroundColor White
Write-Host "  - FLASK_ENV: production" -ForegroundColor White
Write-Host ""
Write-Host "Step 5: Deploy! 🚀" -ForegroundColor Yellow
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  📖 QUICK_NETLIFY_DEPLOY.md - Quick start (3 min)" -ForegroundColor White
Write-Host "  📖 NETLIFY_READY.md - Full overview" -ForegroundColor White
Write-Host "  📖 NETLIFY_DEPLOYMENT.md - Detailed guide" -ForegroundColor White
Write-Host "  📖 DEPLOYMENT_CHECKLIST.md - Pre/post checks" -ForegroundColor White
Write-Host ""
