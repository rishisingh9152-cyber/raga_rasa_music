#!/usr/bin/env pwsh

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "RagaRasa End-to-End Test Suite" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# URLs
$BACKEND_URL = "https://raga-rasa-backend.onrender.com"
$EMOTION_URL = "https://raga-rasa-music.onrender.com"
$FRONTEND_URL = "https://raga-rasa-music-52.vercel.app"

# Test 1: Backend Health
Write-Host "[TEST 1] Backend Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/" -UseBasicParsing -TimeoutSec 10
    Write-Host "✓ Backend is online" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend offline: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Emotion Service Health
Write-Host "[TEST 2] Emotion Service Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$EMOTION_URL/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "✓ Emotion service is online" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "✗ Emotion service offline: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Get Songs from Backend
Write-Host "[TEST 3] Get Songs from Backend" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/songs" -UseBasicParsing -TimeoutSec 10
    $data = $response.Content | ConvertFrom-Json
    $count = $data.songs.Count
    Write-Host "✓ Successfully retrieved songs from database" -ForegroundColor Green
    Write-Host "Total songs: $count" -ForegroundColor Green
    Write-Host "Sample: $($data.songs[0].title) - $($data.songs[0].artist)" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to get songs: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Frontend Status
Write-Host "[TEST 4] Frontend Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$FRONTEND_URL/" -UseBasicParsing -TimeoutSec 10
    Write-Host "✓ Frontend is online" -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Frontend offline: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Test Summary:" -ForegroundColor Cyan
Write-Host "- Backend: Check if all green" -ForegroundColor White
Write-Host "- Emotion Service: Check if responding" -ForegroundColor White
Write-Host "- Database: Check if songs are loading" -ForegroundColor White
Write-Host "- Frontend: Check if accessible" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
