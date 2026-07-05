from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import aiohttp
import threading
import json
import os
import hashlib
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import requests
from urllib.parse import urlencode

app = FastAPI()

class VehicleRequest(BaseModel):
    rc: str

class PasswordRequest(BaseModel):
    password: str

# === VEHICLE API ===
API_BASE = "https://vehicleinfobyterabaap.vercel.app/lookup"
VERSION = "2.0 PRO"
CORRECT_PASSWORD = "Avenue-1"
MAX_ATTEMPTS = 3

# === CACHE SYSTEM ===
def cache_path(rc):
    os.makedirs("cache", exist_ok=True)
    return f"cache/{hashlib.md5(rc.encode()).hexdigest()}.json"

def save_cache(rc, data):
    with open(cache_path(rc), "w") as f:
        json.dump(data, f, indent=4)

def load_cache(rc):
    path = cache_path(rc)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

# === LOGGING ===
def log_query(rc, status):
    os.makedirs("logs", exist_ok=True)
    with open("logs/vehicle_lookup.log", "a") as f:
        f.write(f"[{datetime.now()}] RC: {rc} - Status: {status}\n")

def log_attempt(ip, attempts):
    os.makedirs("logs", exist_ok=True)
    with open("logs/access_attempts.log", "a") as f:
        f.write(f"[{datetime.now()}] IP: {ip} - Attempts: {attempts}\n")

def fetch_vehicle_data(rc):
    cached = load_cache(rc)
    if cached:
        return cached, True

    params = {"rc": rc}
    url = f"{API_BASE}?{urlencode(params)}"

    try:
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "VehicleLookup/PRO"},
        )
    except Exception as e:
        return {"error": str(e)}, False

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}"}, False

    try:
        data = resp.json()
    except:
        return {"error": "Invalid JSON returned by API."}, False

    save_cache(rc, data)
    return data, False

# === SESSION STORAGE ===
session_data = {
    "attempts": 0,
    "locked": False,
    "authenticated": False
}

@app.get("/", response_class=HTMLResponse)
async def index():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Samarth Hacker | Vehicle Lookup</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;800;900&family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Orbitron', sans-serif;
            background: #0a0a0f;
            min-height: 100vh;
            color: #e2e8f0;
            overflow-x: hidden;
        }
        
        /* ===== BACKGROUND ===== */
        .cyber-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background: #0a0a0f;
            background-image: 
                radial-gradient(ellipse at 20% 50%, rgba(0, 255, 0, 0.03) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 50%, rgba(0, 255, 255, 0.02) 0%, transparent 60%);
        }
        .cyber-grid {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0, 255, 0, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 0, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            animation: gridMove 20s linear infinite;
        }
        @keyframes gridMove {
            0% { transform: translate(0, 0); }
            100% { transform: translate(40px, 40px); }
        }
        
        /* ===== GLASS CARDS ===== */
        .glass-premium {
            background: rgba(10, 10, 15, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 0, 0.08);
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.8);
            transition: all 0.3s ease;
        }
        .glass-premium:hover {
            border-color: rgba(0, 255, 0, 0.15);
        }
        
        /* ===== DISCLAIMER ===== */
        .disclaimer-box {
            background: rgba(255, 0, 0, 0.05);
            border: 1px solid rgba(255, 0, 0, 0.15);
            border-radius: 12px;
            padding: 16px 20px;
            text-align: center;
        }
        .disclaimer-box .title {
            color: #ef4444;
            font-weight: 800;
            font-size: 0.8rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }
        .disclaimer-box .text {
            color: #94a3b8;
            font-size: 0.75rem;
            margin-top: 4px;
        }
        
        /* ===== INPUT ===== */
        .input-cyber {
            background: rgba(0, 0, 0, 0.6);
            border: 1.5px solid rgba(0, 255, 0, 0.1);
            transition: all 0.3s ease;
            color: #e2e8f0;
            font-family: 'Orbitron', monospace;
            font-size: 1.2rem;
            letter-spacing: 0.05em;
            padding: 1rem 1.5rem;
            width: 100%;
            border-radius: 12px;
        }
        .input-cyber:focus {
            border-color: #00ff00;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.1), inset 0 0 30px rgba(0, 255, 0, 0.03);
            outline: none;
        }
        .input-cyber::placeholder {
            color: rgba(148, 163, 184, 0.2);
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.02em;
        }
        .input-cyber.error {
            border-color: #ef4444;
            box-shadow: 0 0 30px rgba(239, 68, 68, 0.15);
        }
        .input-cyber.success {
            border-color: #22c55e;
            box-shadow: 0 0 30px rgba(34, 197, 94, 0.15);
        }
        
        /* ===== BUTTONS ===== */
        .btn-cyber {
            background: linear-gradient(135deg, #00aa00, #00ff00);
            border: none;
            border-radius: 12px;
            padding: 1rem 2rem;
            font-weight: 700;
            color: #000000;
            font-family: 'Orbitron', monospace;
            font-size: 0.95rem;
            letter-spacing: 0.05em;
            box-shadow: 0 4px 30px rgba(0, 255, 0, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            width: 100%;
        }
        .btn-cyber:hover {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 8px 50px rgba(0, 255, 0, 0.4);
        }
        .btn-cyber:active {
            transform: scale(0.98);
        }
        .btn-cyber:disabled {
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #cc0000, #ff0000);
            box-shadow: 0 4px 30px rgba(255, 0, 0, 0.2);
            color: white;
        }
        .btn-danger:hover {
            box-shadow: 0 8px 50px rgba(255, 0, 0, 0.4);
        }
        
        .btn-purple {
            background: linear-gradient(135deg, #7c3aed, #8b5cf6);
            box-shadow: 0 4px 30px rgba(124, 58, 237, 0.2);
            color: white;
        }
        .btn-purple:hover {
            box-shadow: 0 8px 50px rgba(124, 58, 237, 0.4);
        }
        
        /* ===== STATUS BADGE ===== */
        .badge-cyber {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 4px 14px;
            border-radius: 100px;
            font-size: 0.6rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 255, 0, 0.1);
            font-family: 'Orbitron', monospace;
        }
        .dot-cyber {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-cyber.idle { background: #22c55e; box-shadow: 0 0 15px rgba(34, 197, 94, 0.3); }
        .dot-cyber.active {
            background: #00ff00;
            animation: pulse-dot 0.8s ease-in-out infinite;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.5);
        }
        .dot-cyber.error {
            background: #ef4444;
            animation: pulse-dot 0.4s ease-in-out infinite;
            box-shadow: 0 0 30px rgba(239, 68, 68, 0.5);
        }
        .dot-cyber.locked {
            background: #dc2626;
            animation: pulse-dot 0.3s ease-in-out infinite;
            box-shadow: 0 0 40px rgba(220, 38, 38, 0.6);
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(0.7); }
        }
        
        /* ===== ACCESS DENIED ANIMATION ===== */
        .access-denied {
            color: #ef4444;
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 1.2rem;
            animation: deniedPulse 1.5s ease-in-out infinite;
            text-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
        }
        @keyframes deniedPulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.98); }
        }
        
        .access-granted {
            color: #22c55e;
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 1.2rem;
            animation: grantedPulse 2s ease-in-out infinite;
            text-shadow: 0 0 30px rgba(34, 197, 94, 0.3);
        }
        @keyframes grantedPulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.02); }
        }
        
        .access-locked {
            color: #dc2626;
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 1.5rem;
            animation: lockedPulse 0.8s ease-in-out infinite;
            text-shadow: 0 0 40px rgba(220, 38, 38, 0.4);
        }
        @keyframes lockedPulse {
            0%, 100% { opacity: 1; transform: scale(1) rotate(-2deg); }
            50% { opacity: 0.6; transform: scale(1.05) rotate(2deg); }
        }
        
        /* ===== RESULTS TABLE ===== */
        .result-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        .result-table tr {
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }
        .result-table tr:last-child {
            border-bottom: none;
        }
        .result-table td {
            padding: 10px 12px;
        }
        .result-table .field {
            color: #00ff00;
            font-weight: 600;
            font-family: 'Orbitron', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            width: 40%;
        }
        .result-table .value {
            color: #e2e8f0;
            font-weight: 400;
            word-break: break-word;
        }
        
        /* ===== LOGS ===== */
        .logs-premium {
            scrollbar-width: thin;
            scrollbar-color: rgba(0, 255, 0, 0.1) transparent;
            max-height: 150px;
            overflow-y: auto;
            font-size: 0.7rem;
            font-family: 'Orbitron', monospace;
        }
        .logs-premium::-webkit-scrollbar { width: 4px; }
        .logs-premium::-webkit-scrollbar-track { background: transparent; }
        .logs-premium::-webkit-scrollbar-thumb {
            background: rgba(0, 255, 0, 0.15);
            border-radius: 10px;
        }
        .log-entry {
            padding: 3px 10px;
            border-left: 2px solid transparent;
            color: #64748b;
            transition: all 0.15s;
        }
        .log-entry:hover {
            background: rgba(0, 255, 0, 0.03);
            border-left-color: #00ff00;
            color: #94a3b8;
        }
        .log-entry.success { color: #22c55e; }
        .log-entry.error { color: #ef4444; }
        .log-entry.info { color: #60a5fa; }
        .log-entry.warning { color: #fbbf24; }
        .log-entry.locked { color: #dc2626; font-weight: 700; }
        
        /* ===== DIVIDER ===== */
        .divider-cyber {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.15), transparent);
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .input-cyber { font-size: 0.95rem; padding: 0.8rem 1rem; }
            .result-table td { padding: 6px 8px; font-size: 0.75rem; }
            .result-table .field { font-size: 0.6rem; }
            .access-denied, .access-granted { font-size: 1rem; }
            .access-locked { font-size: 1.2rem; }
        }
        
        /* ===== BOOTING ANIMATION ===== */
        .booting {
            color: #60a5fa;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            font-size: 0.8rem;
            animation: bootPulse 0.5s ease-in-out infinite;
        }
        @keyframes bootPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
</head>
<body>

    <div class="cyber-bg">
        <div class="cyber-grid"></div>
    </div>

    <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-10">
        
        <!-- ===== HEADER ===== -->
        <header class="text-center mb-8">
            <div class="inline-block px-6 py-2 rounded-full border border-green-500/20 bg-black/30 mb-4">
                <span class="text-[10px] text-green-500 font-['Orbitron'] tracking-[0.15em]">🔐 SECURE • VEHICLE ACCESS</span>
            </div>
            <h1 class="text-4xl lg:text-6xl font-black font-['Orbitron'] tracking-tight">
                <span class="text-green-400">VEHICLE</span>
                <span class="text-white">LOOKUP</span>
            </h1>
            <p class="text-sm text-gray-500 font-['Orbitron'] tracking-[0.2em] mt-2">
                [ <span class="text-green-400">SAMARTH HACKER</span> ]
            </p>
            <div class="divider-cyber w-full max-w-md mx-auto mt-4"></div>
        </header>

        <!-- ===== DISCLAIMER ===== -->
        <div class="disclaimer-box mb-6">
            <div class="title">⚠️ Disclaimer</div>
            <div class="text">This tool is only for educational purposes.<br>Made by: <strong class="text-green-400">Samarth</strong></div>
        </div>

        <!-- ===== MAIN CARD ===== -->
        <div class="glass-premium rounded-2xl p-6 lg:p-8">
            
            <!-- Vehicle Intelligence -->
            <div class="flex items-center gap-3 mb-6">
                <span class="text-2xl">🚗</span>
                <div>
                    <div class="text-xs text-gray-500 font-['Orbitron'] tracking-[0.1em]">VEHICLE INTELLIGENCE</div>
                    <div class="text-xs text-gray-400">Designed Website: <strong class="text-green-400">Samarth</strong> • Website Owner: <strong class="text-green-400">Samarth</strong></div>
                </div>
            </div>

            <!-- Password Section -->
            <div id="passwordSection" class="space-y-4">
                <div>
                    <label class="text-xs text-gray-500 font-['Orbitron'] tracking-[0.1em] block mb-2">ENTER ACCESS PASSWORD</label>
                    <div class="relative">
                        <input id="passwordInput" 
                               type="password"
                               class="input-cyber"
                               placeholder="Enter password"
                               onkeydown="if(event.key==='Enter') verifyPassword()">
                    </div>
                    <div id="passwordFeedback" class="text-xs mt-2 h-5"></div>
                </div>

                <button onclick="verifyPassword()" id="passwordBtn" class="btn-cyber">
                    🔓 ACCESS
                </button>
            </div>

            <!-- Access Status -->
            <div id="accessStatus" class="mt-4 p-3 bg-black/30 rounded-xl border border-white/5 text-center hidden">
                <div id="accessMessage" class="text-sm font-['Orbitron']"></div>
            </div>

            <!-- Main System (Hidden until authenticated) -->
            <div id="mainSystem" class="hidden mt-6">
                <div class="divider-cyber w-full mb-4"></div>

                <!-- Status Badge -->
                <div class="flex items-center justify-between p-3 bg-black/30 rounded-xl border border-white/5 mb-4">
                    <div class="badge-cyber">
                        <span class="dot-cyber idle" id="statusDot"></span>
                        <span id="statusText" class="text-gray-400">SYSTEM READY</span>
                    </div>
                    <div class="text-[10px] text-gray-500 font-['Orbitron']" id="timestamp"></div>
                </div>

                <!-- Vehicle RC Lookup -->
                <div class="space-y-4">
                    <div>
                        <label class="text-xs text-gray-500 font-['Orbitron'] tracking-[0.1em] block mb-2">VEHICLE RC LOOKUP</label>
                        <div class="relative">
                            <input id="rcInput" 
                                   class="input-cyber"
                                   placeholder="ENTER RC NUMBER"
                                   onkeydown="if(event.key==='Enter') lookupVehicle()">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <button onclick="lookupVehicle()" id="scanBtn" class="btn-cyber">
                            🔍 SCAN
                        </button>
                        <button onclick="clearResults()" id="clearBtn" class="btn-cyber btn-danger">
                            ✕ CLEAR
                        </button>
                    </div>
                </div>

                <!-- ===== RESULTS SECTION ===== -->
                <div id="resultsSection" class="mt-6 hidden">
                    <div class="divider-cyber w-full mb-4"></div>
                    
                    <!-- Tool Info -->
                    <div class="text-center mb-4">
                        <span class="text-xs text-green-400 font-['Orbitron'] tracking-[0.1em]">⚡ VEHICLE LOOKUP SYSTEM</span>
                        <div class="text-[10px] text-gray-500 mt-1">[ SAMARTH HACKER ]</div>
                    </div>

                    <!-- API Status -->
                    <div id="apiStatus" class="flex items-center justify-between p-3 bg-black/30 rounded-xl border border-white/5 mb-4">
                        <div>
                            <span class="text-xs text-green-400 font-['Orbitron']">API: <span id="apiStatusText">OK</span></span>
                            <span class="text-xs text-gray-500 ml-4">Cached: <span id="cacheStatus">NO</span></span>
                        </div>
                        <div>
                            <span class="text-xs text-gray-500">Response: <span id="responseTime" class="text-green-400">--</span> ms</span>
                        </div>
                    </div>

                    <!-- Results Table -->
                    <div id="resultsTable" class="bg-black/30 rounded-xl border border-white/5 overflow-hidden">
                        <table class="result-table">
                            <tbody id="resultsBody">
                                <tr><td colspan="2" class="text-center text-gray-500 py-8">No data loaded</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Export & Copy -->
                    <div class="grid grid-cols-2 gap-3 mt-4">
                        <button onclick="exportResult()" id="exportBtn" class="btn-cyber text-xs py-2.5 btn-purple">
                            📥 EXPORT JSON
                        </button>
                        <button onclick="copyResult()" id="copyBtn" class="btn-cyber text-xs py-2.5" style="background: linear-gradient(135deg, #7c3aed, #8b5cf6); box-shadow: 0 4px 30px rgba(124, 58, 237, 0.2);">
                            📋 COPY
                        </button>
                    </div>

                    <!-- Logs -->
                    <div class="mt-4">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-[10px] text-gray-500 font-['Orbitron'] tracking-[0.1em]">📜 ACTIVITY LOG</span>
                            <span class="text-[10px] text-gray-500">LIVE</span>
                        </div>
                        <div id="logsContainer" class="logs-premium bg-black/30 rounded-xl p-3 border border-white/5">
                            <div class="log-entry info">🟢 System initialized</div>
                            <div class="log-entry info">⏳ Waiting for RC input...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ===== FOOTER ===== -->
        <footer class="mt-8 pt-4 border-t border-white/5 text-center">
            <p class="text-[10px] text-gray-600 font-['Orbitron'] tracking-[0.1em]">
                ⚡ SAMARTH HACKER • VEHICLE INTELLIGENCE SYSTEM v2.0 PRO
            </p>
            <p class="text-[8px] text-gray-700 mt-1">Made with ❤️ by Samarth</p>
        </footer>
    </div>

    <script>
        let currentData = null;
        let currentRc = null;
        let attempts = 0;
        const maxAttempts = 3;
        const correctPassword = "Avenue-1";

        // ===== PASSWORD VERIFICATION =====
        async function verifyPassword() {
            const passwordInput = document.getElementById('passwordInput');
            const password = passwordInput.value.trim();
            const feedback = document.getElementById('passwordFeedback');
            const statusDiv = document.getElementById('accessStatus');
            const messageDiv = document.getElementById('accessMessage');

            if (!password) {
                feedback.innerHTML = '<span class="text-red-400 text-xs">⚠️ Please enter the password</span>';
                return;
            }

            try {
                const response = await fetch('/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: password })
                });
                const data = await response.json();

                if (data.status === 'success') {
                    // Password correct - Access Granted
                    feedback.innerHTML = '<span class="text-emerald-400 text-xs">✅ Access Granted!</span>';
                    passwordInput.className = 'input-cyber success';
                    document.getElementById('passwordBtn').disabled = true;
                    
                    messageDiv.innerHTML = '<span class="access-granted">✅ ACCESS GRANTED</span>';
                    statusDiv.classList.remove('hidden');
                    
                    // Show main system
                    document.getElementById('passwordSection').classList.add('hidden');
                    document.getElementById('mainSystem').classList.remove('hidden');
                    
                    addLog('🔓 ACCESS GRANTED - System unlocked', 'success');
                    
                    // Reset attempts
                    attempts = 0;
                } else {
                    // Password incorrect
                    attempts = data.attempts || (attempts + 1);
                    const remaining = maxAttempts - attempts;
                    
                    feedback.innerHTML = `<span class="text-red-400 text-xs">❌ Wrong password! ${remaining} attempts remaining</span>`;
                    passwordInput.className = 'input-cyber error';
                    passwordInput.value = '';
                    
                    messageDiv.innerHTML = `<span class="access-denied">🚫 ACCESS DENIED ${attempts}/${maxAttempts}</span>`;
                    statusDiv.classList.remove('hidden');
                    
                    addLog(`🔐 ACCESS DENIED (${attempts}/${maxAttempts})`, 'error');

                    if (attempts >= maxAttempts) {
                        // Locked out
                        messageDiv.innerHTML = '<span class="access-locked">🔒 SYSTEM LOCKED</span>';
                        document.getElementById('passwordBtn').disabled = true;
                        passwordInput.disabled = true;
                        passwordInput.className = 'input-cyber error';
                        feedback.innerHTML = '<span class="text-red-400 text-xs">🔒 System locked. Please restart.</span>';
                        addLog('🔒 SYSTEM LOCKED - Maximum attempts exceeded', 'locked');
                        
                        // Show booting message
                        document.querySelector('.badge-cyber').innerHTML = `
                            <span class="dot-cyber locked"></span>
                            <span class="text-red-500 font-['Orbitron'] booting">🔴 SYSTEM LOCKED</span>
                        `;
                    }
                }
            } catch (error) {
                feedback.innerHTML = `<span class="text-red-400 text-xs">❌ Error: ${error.message}</span>`;
            }
        }

        // ===== TIMESTAMP =====
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('timestamp').textContent = now.toLocaleTimeString('en-US', { 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
            });
        }
        setInterval(updateTimestamp, 1000);
        updateTimestamp();

        // ===== LOGS =====
        function addLog(message, type = 'info') {
            const container = document.getElementById('logsContainer');
            if (!container) return;
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            container.appendChild(entry);
            
            while (container.children.length > 20) {
                container.removeChild(container.firstChild);
            }
            container.scrollTop = container.scrollHeight;
        }

        // ===== LOOKUP VEHICLE =====
        async function lookupVehicle() {
            const rc = document.getElementById('rcInput').value.trim();
            if (!rc) {
                addLog('❌ Please enter an RC number', 'error');
                return;
            }

            document.getElementById('statusText').textContent = 'SEARCHING...';
            document.getElementById('statusText').style.color = '#60a5fa';
            document.getElementById('statusDot').className = 'dot-cyber active';
            
            addLog(`🔍 Searching for RC: ${rc}`, 'info');

            try {
                const response = await fetch('/lookup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rc: rc })
                });
                const data = await response.json();

                if (data.status === 'success') {
                    currentData = data.data;
                    currentRc = rc;
                    displayResults(rc, data.data, data.cached, data.response_time);
                    addLog(`✅ Vehicle found for RC: ${rc}`, 'success');
                    
                    document.getElementById('statusText').textContent = 'SUCCESS';
                    document.getElementById('statusText').style.color = '#22c55e';
                    document.getElementById('statusDot').className = 'dot-cyber active';
                    document.getElementById('statusDot').style.background = '#22c55e';
                } else {
                    addLog(`❌ Error: ${data.message}`, 'error');
                    document.getElementById('statusText').textContent = 'ERROR';
                    document.getElementById('statusText').style.color = '#ef4444';
                    document.getElementById('statusDot').className = 'dot-cyber error';
                }
            } catch (error) {
                addLog(`❌ Request failed: ${error.message}`, 'error');
                document.getElementById('statusText').textContent = 'ERROR';
                document.getElementById('statusText').style.color = '#ef4444';
                document.getElementById('statusDot').className = 'dot-cyber error';
            }
        }

        // ===== DISPLAY RESULTS =====
        function displayResults(rc, data, cached, responseTime) {
            document.getElementById('resultsSection').classList.remove('hidden');
            
            document.getElementById('apiStatusText').textContent = 'OK';
            document.getElementById('apiStatusText').style.color = '#22c55e';
            document.getElementById('cacheStatus').textContent = cached ? 'YES' : 'NO';
            document.getElementById('responseTime').textContent = responseTime || '--';

            const tbody = document.getElementById('resultsBody');
            tbody.innerHTML = '';

            const excludeFields = ['_api_time', 'cached', 'timestamp'];
            
            let hasData = false;
            for (const [key, value] of Object.entries(data)) {
                if (excludeFields.includes(key)) continue;
                if (key.startsWith('_')) continue;
                if (value === null || value === undefined || value === '') continue;
                
                hasData = true;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="field">${key.replace(/_/g, ' ').toUpperCase()}</td>
                    <td class="value">${typeof value === 'object' ? JSON.stringify(value) : value}</td>
                `;
                tbody.appendChild(tr);
            }

            if (!hasData) {
                tbody.innerHTML = `<tr><td colspan="2" class="text-center text-gray-500 py-8">No vehicle data found</td></tr>`;
            }
        }

        // ===== CLEAR RESULTS =====
        function clearResults() {
            document.getElementById('resultsSection').classList.add('hidden');
            document.getElementById('rcInput').value = '';
            document.getElementById('statusText').textContent = 'SYSTEM READY';
            document.getElementById('statusText').style.color = '';
            document.getElementById('statusDot').className = 'dot-cyber idle';
            document.getElementById('statusDot').style.background = '';
            currentData = null;
            currentRc = null;
            
            document.getElementById('logsContainer').innerHTML = `
                <div class="log-entry info">🟢 System initialized</div>
                <div class="log-entry info">⏳ Waiting for RC input...</div>
            `;
            
            addLog('🧹 Results cleared', 'info');
        }

        // ===== EXPORT RESULT =====
        function exportResult() {
            if (!currentData) {
                alert('No data to export. Please lookup a vehicle first.');
                return;
            }
            
            const data = {
                rc: currentRc,
                timestamp: new Date().toISOString(),
                data: currentData
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `vehicle_${currentRc}_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            addLog(`📥 Exported data for ${currentRc}`, 'success');
        }

        // ===== COPY RESULT =====
        function copyResult() {
            if (!currentData) {
                alert('No data to copy. Please lookup a vehicle first.');
                return;
            }
            
            const text = JSON.stringify(currentData, null, 2);
            navigator.clipboard.writeText(text).then(() => {
                addLog(`📋 Copied data for ${currentRc} to clipboard`, 'success');
                const btn = document.getElementById('copyBtn');
                const originalText = btn.textContent;
                btn.textContent = '✅ COPIED!';
                setTimeout(() => { btn.textContent = originalText; }, 2000);
            }).catch(() => {
                addLog('❌ Failed to copy data', 'error');
            });
        }

        // ===== INIT =====
        document.addEventListener('DOMContentLoaded', function() {
            // Password input enter key
            document.getElementById('passwordInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    verifyPassword();
                }
            });
            
            // RC input enter key
            document.getElementById('rcInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    lookupVehicle();
                }
            });
            
            addLog('🟢 Vehicle Lookup System ready', 'info');
            addLog('🔐 Enter password to unlock', 'info');
        });
    </script>
</body>
</html>
    """
    return html

@app.post("/verify")
async def verify_password(request: Request):
    try:
        body = await request.json()
        password = body.get('password', '')
        
        # Get client IP for logging
        client_ip = request.client.host if request.client else "unknown"
        
        if session_data["locked"]:
            return {
                "status": "error",
                "message": "System locked",
                "locked": True,
                "attempts": session_data["attempts"]
            }
        
        if password == CORRECT_PASSWORD:
            session_data["authenticated"] = True
            session_data["attempts"] = 0
            log_attempt(client_ip, session_data["attempts"])
            return {
                "status": "success",
                "message": "Access granted",
                "attempts": session_data["attempts"]
            }
        else:
            session_data["attempts"] += 1
            log_attempt(client_ip, session_data["attempts"])
            
            if session_data["attempts"] >= MAX_ATTEMPTS:
                session_data["locked"] = True
                return {
                    "status": "error",
                    "message": "System locked",
                    "locked": True,
                    "attempts": session_data["attempts"]
                }
            
            return {
                "status": "error",
                "message": "Wrong password",
                "attempts": session_data["attempts"],
                "remaining": MAX_ATTEMPTS - session_data["attempts"]
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/lookup")
async def lookup_vehicle(request: Request):
    try:
        if not session_data["authenticated"]:
            return {"status": "error", "message": "Access denied. Please authenticate first."}
        
        body = await request.json()
        rc = body.get('rc', '').strip()
        
        if not rc:
            return {"status": "error", "message": "RC number is required"}
        
        # Check cache
        cached_data = load_cache(rc)
        if cached_data:
            return {
                "status": "success",
                "data": cached_data,
                "cached": True,
                "response_time": 0
            }
        
        # Fetch from API
        params = {"rc": rc}
        url = f"{API_BASE}?{urlencode(params)}"
        
        start_time = datetime.now()
        try:
            resp = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": "VehicleLookup/PRO"}
            )
        except Exception as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if resp.status_code != 200:
            return {
                "status": "error",
                "message": f"HTTP {resp.status_code}: {resp.text[:100]}"
            }
        
        try:
            data = resp.json()
        except:
            return {"status": "error", "message": "Invalid JSON response from API"}
        
        # Save cache
        save_cache(rc, data)
        log_query(rc, "SUCCESS")
        
        return {
            "status": "success",
            "data": data,
            "cached": False,
            "response_time": round(response_time, 2)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚗 Samarth Hacker — Vehicle Lookup System")
    print("🔐 Password: Avenue-1")
    print("🌐 http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
