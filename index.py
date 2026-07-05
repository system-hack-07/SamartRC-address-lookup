from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

# === SESSION STORAGE ===
session_data = {
    "attempts": 0,
    "locked": False,
    "authenticated": False
}

# === CACHE SYSTEM ===
def cache_path(rc):
    cache_dir = "/tmp/cache"
    os.makedirs(cache_dir, exist_ok=True)
    return f"{cache_dir}/{hashlib.md5(rc.encode()).hexdigest()}.json"

def save_cache(rc, data):
    try:
        with open(cache_path(rc), "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

def load_cache(rc):
    try:
        path = cache_path(rc)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except:
        pass
    return None

# === LOGGING ===
def log_query(rc, status):
    try:
        log_dir = "/tmp/logs"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/vehicle_lookup.log", "a") as f:
            f.write(f"[{datetime.now()}] RC: {rc} - Status: {status}\n")
    except:
        pass

def log_attempt(ip, attempts):
    try:
        log_dir = "/tmp/logs"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/access_attempts.log", "a") as f:
            f.write(f"[{datetime.now()}] IP: {ip} - Attempts: {attempts}\n")
    except:
        pass

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
        .cyber-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background: #0a0a0f;
            background-image: 
                radial-gradient(ellipse at 20% 50%, rgba(59, 130, 246, 0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 50%, rgba(99, 102, 241, 0.05) 0%, transparent 60%),
                radial-gradient(ellipse at 50% 100%, rgba(139, 92, 246, 0.03) 0%, transparent 50%);
        }
        .cyber-grid {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            animation: gridMove 20s linear infinite;
        }
        @keyframes gridMove {
            0% { transform: translate(0, 0); }
            100% { transform: translate(40px, 40px); }
        }
        .glass-premium {
            background: rgba(10, 10, 15, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 2px solid rgba(59, 130, 246, 0.3);
            box-shadow: 
                0 20px 40px -12px rgba(0, 0, 0, 0.8),
                0 0 30px rgba(59, 130, 246, 0.05),
                inset 0 0 30px rgba(59, 130, 246, 0.02);
            transition: all 0.3s ease;
            animation: glowPulse 3s ease-in-out infinite;
        }
        .glass-premium:hover {
            border-color: rgba(59, 130, 246, 0.7);
            box-shadow: 
                0 20px 40px -12px rgba(0, 0, 0, 0.8),
                0 0 60px rgba(59, 130, 246, 0.15),
                0 0 100px rgba(59, 130, 246, 0.08),
                inset 0 0 50px rgba(59, 130, 246, 0.05);
        }
        @keyframes glowPulse {
            0%, 100% { 
                border-color: rgba(59, 130, 246, 0.3);
                box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.8), 0 0 30px rgba(59, 130, 246, 0.05);
            }
            50% { 
                border-color: rgba(59, 130, 246, 0.6);
                box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.8), 0 0 60px rgba(59, 130, 246, 0.1), 0 0 100px rgba(59, 130, 246, 0.05);
            }
        }
        .sprinkle-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9998;
            overflow: hidden;
        }
        .sprinkle {
            position: absolute;
            animation: sprinkleFall linear forwards;
            pointer-events: none;
            font-size: 1.5rem;
            text-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
        }
        @keyframes sprinkleFall {
            0% { transform: translateY(-10px) rotate(0deg) scale(0.3); opacity: 1; }
            100% { transform: translateY(110vh) rotate(720deg) scale(1.5); opacity: 0; }
        }
        .boot-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 99999;
            background: #0a0a0f;
            display: none;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .boot-overlay.active {
            display: flex;
            animation: bootFade 4s ease-out forwards;
        }
        @keyframes bootFade {
            0% { opacity: 1; }
            80% { opacity: 1; }
            100% { opacity: 0; }
        }
        .boot-text {
            font-family: 'Orbitron', monospace;
            color: #60a5fa;
            font-size: 1.2rem;
            letter-spacing: 0.15em;
            animation: bootPulse 0.5s ease-in-out infinite;
        }
        @keyframes bootPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .boot-progress {
            width: 300px;
            height: 4px;
            background: rgba(59, 130, 246, 0.1);
            border-radius: 10px;
            margin-top: 20px;
            overflow: hidden;
        }
        .boot-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #60a5fa, #3b82f6);
            border-radius: 10px;
            animation: bootProgress 3s ease-in-out forwards;
            width: 0%;
        }
        @keyframes bootProgress {
            0% { width: 0%; }
            20% { width: 15%; }
            40% { width: 35%; }
            60% { width: 55%; }
            80% { width: 80%; }
            100% { width: 100%; }
        }
        .boot-dots::after {
            content: '';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0% { content: ''; }
            25% { content: '.'; }
            50% { content: '..'; }
            75% { content: '...'; }
            100% { content: ''; }
        }
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
        .input-cyber {
            background: rgba(0, 0, 0, 0.6);
            border: 1.5px solid rgba(59, 130, 246, 0.2);
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
            border-color: #3b82f6;
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.2), inset 0 0 30px rgba(59, 130, 246, 0.05);
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
        .btn-cyber {
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            border: none;
            border-radius: 12px;
            padding: 1rem 2rem;
            font-weight: 700;
            color: #ffffff;
            font-family: 'Orbitron', monospace;
            font-size: 0.95rem;
            letter-spacing: 0.05em;
            box-shadow: 0 4px 30px rgba(59, 130, 246, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        .btn-cyber::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
            transform: scale(0);
            transition: transform 0.6s;
        }
        .btn-cyber:hover::after {
            transform: scale(1);
        }
        .btn-cyber:hover {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 8px 50px rgba(59, 130, 246, 0.5);
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
            background: linear-gradient(135deg, #dc2626, #ef4444);
            box-shadow: 0 4px 30px rgba(239, 68, 68, 0.2);
            color: white;
        }
        .btn-danger:hover {
            box-shadow: 0 8px 50px rgba(239, 68, 68, 0.4);
        }
        .btn-purple {
            background: linear-gradient(135deg, #7c3aed, #8b5cf6);
            box-shadow: 0 4px 30px rgba(124, 58, 237, 0.2);
            color: white;
        }
        .btn-purple:hover {
            box-shadow: 0 8px 50px rgba(124, 58, 237, 0.4);
        }
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
            border: 1px solid rgba(59, 130, 246, 0.15);
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
            background: #3b82f6;
            animation: pulse-dot 0.8s ease-in-out infinite;
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
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
            color: #60a5fa;
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
        .logs-premium {
            scrollbar-width: thin;
            scrollbar-color: rgba(59, 130, 246, 0.1) transparent;
            max-height: 150px;
            overflow-y: auto;
            font-size: 0.7rem;
            font-family: 'Orbitron', monospace;
        }
        .logs-premium::-webkit-scrollbar { width: 4px; }
        .logs-premium::-webkit-scrollbar-track { background: transparent; }
        .logs-premium::-webkit-scrollbar-thumb {
            background: rgba(59, 130, 246, 0.15);
            border-radius: 10px;
        }
        .log-entry {
            padding: 3px 10px;
            border-left: 2px solid transparent;
            color: #64748b;
            transition: all 0.15s;
        }
        .log-entry:hover {
            background: rgba(59, 130, 246, 0.03);
            border-left-color: #3b82f6;
            color: #94a3b8;
        }
        .log-entry.success { color: #22c55e; }
        .log-entry.error { color: #ef4444; }
        .log-entry.info { color: #60a5fa; }
        .log-entry.warning { color: #fbbf24; }
        .log-entry.locked { color: #dc2626; font-weight: 700; }
        .divider-cyber {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.15), transparent);
        }
        @media (max-width: 768px) {
            .input-cyber { font-size: 0.95rem; padding: 0.8rem 1rem; }
            .result-table td { padding: 6px 8px; font-size: 0.75rem; }
            .result-table .field { font-size: 0.6rem; }
            .access-denied, .access-granted { font-size: 1rem; }
            .access-locked { font-size: 1.2rem; }
            .boot-text { font-size: 0.9rem; }
            .boot-progress { width: 200px; }
        }
    </style>
</head>
<body>

    <!-- BOOT OVERLAY -->
    <div class="boot-overlay" id="bootOverlay">
        <div class="boot-text">🚀 INITIALIZING SYSTEM<span class="boot-dots"></span></div>
        <div class="boot-progress">
            <div class="boot-progress-fill"></div>
        </div>
        <div class="boot-text" style="font-size: 0.8rem; margin-top: 10px; color: #64748b;">Loading Vehicle Intelligence...</div>
    </div>

    <!-- SPRINKLE CONTAINER -->
    <div class="sprinkle-container" id="sprinkleContainer"></div>

    <!-- AUDIO -->
    <audio id="clickSound" preload="auto">
        <source src="data:audio/wav;base64,UklGRlYDAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQYDAACBhYqFh4qAgICAf4mMjo6LgH6Af3t/gHp3doR/gXx2e3Z1c2dxc3NwZWNfXmNcU1hVU1dWU1BQUU1MSkVGRkpHSEZGQ0dDQkI+OjUyMy4rKScnJiMiHRsWGRIPDAkGBwMCAQABAgIDAwMCAgEBAQEBAQEBAgIDAgIDAgIDAwMDAwMEBAQEBQUFBQUGBgYGBwcHCAgJCQkJCwsLCwsLCwwMDA0NDQ4ODg8PDw8PDw8PDw8PDw8PDw8QDw8PDw4ODg0NDQwMDAwLCwsKCgoICQgHBwYGBgUEBAMDAwICAQEBAQEBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDxAPEA8PDw8PDw8PDw8OEA8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoKCQkJCQgHBwYGBgUFBAMDAwMCAgIBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDw8QDw8PDw8PDw8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoJCQkICAcHBwYGBQUEBAMDAwMCAgEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBwcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PEA8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAA==">
        </source>
    </audio>
    <audio id="errorSound" preload="auto">
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFh4qAgICAf4mMjo6LgH6Af3t/gHp3doR/gXx2e3Z1c2dxc3NwZWNfXmNcU1hVU1dWU1BQUU1MSkVGRkpHSEZGQ0dDQkI+OjUyMy4rKScnJiMiHRsWGRIPDAkGBwMCAQABAgIDAwMCAgEBAQEBAQEBAgIDAgIDAgIDAwMDAwMEBAQEBQUFBQUGBgYGBwcHCAgJCQkJCwsLCwsLCwwMDA0NDQ4ODg8PDw8PDw8PDw8PDw8PDw8QDw8PDw4ODg0NDQwMDAwLCwsKCgoICQgHBwYGBgUEBAMDAwICAQEBAQEBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDxAPEA8PDw8PDw8PDw8OEA8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoKCQkJCQgHBwYGBgUFBAMDAwMCAgIBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDw8QDw8PDw8PDw8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoJCQkICAcHBwYGBQUEBAMDAwMCAgEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBwcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PEA8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAA==">
        </source>
    </audio>
    <audio id="successSound" preload="auto">
        <source src="data:audio/wav;base64,UklGRsYDAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQYDAACBhYqFh4qAgICAf4mMjo6LgH6Af3t/gHp3doR/gXx2e3Z1c2dxc3NwZWNfXmNcU1hVU1dWU1BQUU1MSkVGRkpHSEZGQ0dDQkI+OjUyMy4rKScnJiMiHRsWGRIPDAkGBwMCAQABAgIDAwMCAgEBAQEBAQEBAgIDAgIDAgIDAwMDAwMEBAQEBQUFBQUGBgYGBwcHCAgJCQkJCwsLCwsLCwwMDA0NDQ4ODg8PDw8PDw8PDw8PDw8PDw8QDw8PDw4ODg0NDQwMDAwLCwsKCgoICQgHBwYGBgUEBAMDAwICAQEBAQEBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDxAPEA8PDw8PDw8PDw8OEA8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoKCQkJCQgHBwYGBgUFBAMDAwMCAgIBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDw8QDw8PDw8PDw8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoJCQkICAcHBwYGBQUEBAMDAwMCAgEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBwcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PEA8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAA==">
        </source>
    </audio>
    <audio id="bootSound" preload="auto">
        <source src="data:audio/wav;base64,UklGRlYDAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQYDAACBhYqFh4qAgICAf4mMjo6LgH6Af3t/gHp3doR/gXx2e3Z1c2dxc3NwZWNfXmNcU1hVU1dWU1BQUU1MSkVGRkpHSEZGQ0dDQkI+OjUyMy4rKScnJiMiHRsWGRIPDAkGBwMCAQABAgIDAwMCAgEBAQEBAQEBAgIDAgIDAgIDAwMDAwMEBAQEBQUFBQUGBgYGBwcHCAgJCQkJCwsLCwsLCwwMDA0NDQ4ODg8PDw8PDw8PDw8PDw8PDw8QDw8PDw4ODg0NDQwMDAwLCwsKCgoICQgHBwYGBgUEBAMDAwICAQEBAQEBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDxAPEA8PDw8PDw8PDw8OEA8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoKCQkJCQgHBwYGBgUFBAMDAwMCAgIBAQEBAQECAgIDAwMDAwQEBAUFBQYGBwcHCAgICQkJCgoLCwwMDA0ODQ4PDw8PDw8QDw8PDw8PDw8PDw4ODg4ODQ0NDQwMDAwLCwsLCgoJCQkICAcHBwYGBQUEBAMDAwMCAgEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBwcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PEA8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAQEBAQECAgIDAwMDAwQEBAUFBQUGBgcHCAgICQkJCgoLCwsLDAwMDQ0NDg4ODw8PDw8PDw8PDw4ODg4ODQ0NDQ0MDAwLCwsLCgoKCQkJCQgHBwcGBgUFBQQEAwMDAwICAQEBAA==">
        </source>
    </audio>

    <div class="cyber-bg">
        <div class="cyber-grid"></div>
    </div>

    <div class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-10">
        
        <header class="text-center mb-8">
            <div class="inline-block px-6 py-2 rounded-full border border-blue-500/20 bg-black/30 mb-4">
                <span class="text-[10px] text-blue-400 font-['Orbitron'] tracking-[0.15em]">🔐 SECURE • VEHICLE ACCESS</span>
            </div>
            <h1 class="text-4xl lg:text-6xl font-black font-['Orbitron'] tracking-tight">
                <span class="text-blue-400">VEHICLE</span>
                <span class="text-white">LOOKUP</span>
            </h1>
            <p class="text-sm text-gray-500 font-['Orbitron'] tracking-[0.2em] mt-2">
                [ <span class="text-blue-400">SAMARTH HACKER</span> ]
            </p>
            <div class="divider-cyber w-full max-w-md mx-auto mt-4"></div>
        </header>

        <!-- DISCLAIMER -->
        <div class="disclaimer-box mb-6">
            <div class="title">⚠️ Disclaimer</div>
            <div class="text">This tool is only for educational purposes.<br>Made by: <strong class="text-blue-400">Samarth</strong></div>
        </div>

        <!-- MAIN PANEL -->
        <div class="glass-premium rounded-2xl p-6 lg:p-8" id="mainPanel">
            
            <div class="flex items-center gap-3 mb-6">
                <span class="text-2xl">🚗</span>
                <div>
                    <div class="text-xs text-gray-500 font-['Orbitron'] tracking-[0.1em]">VEHICLE INTELLIGENCE</div>
                    <div class="text-xs text-gray-400">Designed Website: <strong class="text-blue-400">Samarth</strong> • Website Owner: <strong class="text-blue-400">Samarth</strong></div>
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

            <div id="accessStatus" class="mt-4 p-3 bg-black/30 rounded-xl border border-blue-500/10 text-center hidden">
                <div id="accessMessage" class="text-sm font-['Orbitron']"></div>
            </div>

            <!-- Main System -->
            <div id="mainSystem" class="hidden mt-6">
                <div class="divider-cyber w-full mb-4"></div>

                <div class="flex items-center justify-between p-3 bg-black/30 rounded-xl border border-blue-500/10 mb-4">
                    <div class="badge-cyber">
                        <span class="dot-cyber idle" id="statusDot"></span>
                        <span id="statusText" class="text-gray-400">SYSTEM READY</span>
                    </div>
                    <div class="text-[10px] text-gray-500 font-['Orbitron']" id="timestamp"></div>
                </div>

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

                <div id="resultsSection" class="mt-6 hidden">
                    <div class="divider-cyber w-full mb-4"></div>
                    
                    <div class="text-center mb-4">
                        <span class="text-xs text-blue-400 font-['Orbitron'] tracking-[0.1em]">⚡ VEHICLE LOOKUP SYSTEM</span>
                        <div class="text-[10px] text-gray-500 mt-1">[ SAMARTH HACKER ]</div>
                    </div>

                    <div id="apiStatus" class="flex items-center justify-between p-3 bg-black/30 rounded-xl border border-blue-500/10 mb-4">
                        <div>
                            <span class="text-xs text-blue-400 font-['Orbitron']">API: <span id="apiStatusText">OK</span></span>
                            <span class="text-xs text-gray-500 ml-4">Cached: <span id="cacheStatus">NO</span></span>
                        </div>
                        <div>
                            <span class="text-xs text-gray-500">Response: <span id="responseTime" class="text-blue-400">--</span> ms</span>
                        </div>
                    </div>

                    <div id="resultsTable" class="bg-black/30 rounded-xl border border-blue-500/10 overflow-hidden">
                        <table class="result-table">
                            <tbody id="resultsBody">
                                <tr><td colspan="2" class="text-center text-gray-500 py-8">No data loaded</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="grid grid-cols-2 gap-3 mt-4">
                        <button onclick="exportResult()" id="exportBtn" class="btn-cyber text-xs py-2.5 btn-purple">
                            📥 EXPORT JSON
                        </button>
                        <button onclick="copyResult()" id="copyBtn" class="btn-cyber text-xs py-2.5" style="background: linear-gradient(135deg, #1e40af, #3b82f6); box-shadow: 0 4px 30px rgba(59, 130, 246, 0.2);">
                            📋 COPY
                        </button>
                    </div>

                    <div class="mt-4">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-[10px] text-gray-500 font-['Orbitron'] tracking-[0.1em]">📜 ACTIVITY LOG</span>
                            <span class="text-[10px] text-gray-500">LIVE</span>
                        </div>
                        <div id="logsContainer" class="logs-premium bg-black/30 rounded-xl p-3 border border-blue-500/10">
                            <div class="log-entry info">🟢 System initialized</div>
                            <div class="log-entry info">⏳ Waiting for RC input...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FOOTER -->
        <footer class="mt-8 pt-4 border-t border-white/5 text-center">
            <p class="text-[10px] text-gray-600 font-['Orbitron'] tracking-[0.1em]">
                ⚡ SAMARTH HACKER • VEHICLE INTELLIGENCE SYSTEM v2.0 PRO
            </p>
            <p class="text-[10px] text-blue-400 font-['Orbitron'] tracking-[0.1em] mt-1">
                👑 OWNER: <strong class="text-blue-400">SAMARTH</strong>
            </p>
        </footer>
    </div>

    <script>
        let currentData = null;
        let currentRc = null;
        let attempts = 0;
        const maxAttempts = 3;
        const correctPassword = "Avenue-1";

        // === SOUND FUNCTIONS ===
        function playSound(id) {
            try {
                const audio = document.getElementById(id);
                if (audio) {
                    audio.currentTime = 0;
                    audio.play().catch(() => {});
                }
            } catch(e) {}
        }
        function playClickSound() { playSound('clickSound'); }
        function playErrorSound() { playSound('errorSound'); }
        function playSuccessSound() { playSound('successSound'); }
        function playBootSound() { playSound('bootSound'); }

        // === SPRINKLE EFFECT ===
        function triggerSprinkles() {
            const container = document.getElementById('sprinkleContainer');
            container.innerHTML = '';
            const emojis = ['🔵', '💠', '✨', '⭐', '🔹', '💎', '🌟', '⚡', '💫', '🌀'];
            for (let i = 0; i < 40; i++) {
                const sprinkle = document.createElement('div');
                sprinkle.className = 'sprinkle';
                sprinkle.textContent = emojis[Math.floor(Math.random() * emojis.length)];
                sprinkle.style.left = Math.random() * 100 + '%';
                sprinkle.style.top = '-10px';
                sprinkle.style.fontSize = (0.8 + Math.random() * 1.8) + 'rem';
                sprinkle.style.animationDuration = (2 + Math.random() * 3) + 's';
                sprinkle.style.animationDelay = (Math.random() * 1.5) + 's';
                container.appendChild(sprinkle);
            }
            setTimeout(() => { container.innerHTML = ''; }, 5000);
        }

        // === FAKE BOOTING ===
        function showBooting() {
            return new Promise((resolve) => {
                const overlay = document.getElementById('bootOverlay');
                overlay.classList.remove('active');
                void overlay.offsetWidth;
                overlay.classList.add('active');
                playBootSound();
                const fill = document.querySelector('.boot-progress-fill');
                fill.style.animation = 'none';
                void fill.offsetWidth;
                fill.style.animation = 'bootProgress 3s ease-in-out forwards';
                setTimeout(() => {
                    overlay.classList.remove('active');
                    resolve();
                }, 4000);
            });
        }

        // === VERIFY PASSWORD ===
        async function verifyPassword() {
            const passwordInput = document.getElementById('passwordInput');
            const password = passwordInput.value.trim();
            const feedback = document.getElementById('passwordFeedback');
            const statusDiv = document.getElementById('accessStatus');
            const messageDiv = document.getElementById('accessMessage');

            if (!password) {
                feedback.innerHTML = '<span class="text-red-400 text-xs">⚠️ Please enter the password</span>';
                playErrorSound();
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
                    feedback.innerHTML = '<span class="text-emerald-400 text-xs">✅ Access Granted!</span>';
                    passwordInput.className = 'input-cyber success';
                    document.getElementById('passwordBtn').disabled = true;
                    messageDiv.innerHTML = '<span class="access-granted">✅ ACCESS GRANTED</span>';
                    statusDiv.classList.remove('hidden');
                    playSuccessSound();
                    triggerSprinkles();
                    await showBooting();
                    document.getElementById('passwordSection').classList.add('hidden');
                    document.getElementById('mainSystem').classList.remove('hidden');
                    addLog('🔓 ACCESS GRANTED - System unlocked', 'success');
                    attempts = 0;
                } else {
                    attempts = data.attempts || (attempts + 1);
                    const remaining = maxAttempts - attempts;
                    feedback.innerHTML = `<span class="text-red-400 text-xs">❌ Wrong password! ${remaining} attempts remaining</span>`;
                    passwordInput.className = 'input-cyber error';
                    passwordInput.value = '';
                    messageDiv.innerHTML = `<span class="access-denied">🚫 ACCESS DENIED ${attempts}/${maxAttempts}</span>`;
                    statusDiv.classList.remove('hidden');
                    playErrorSound();
                    addLog(`🔐 ACCESS DENIED (${attempts}/${maxAttempts})`, 'error');

                    if (attempts >= maxAttempts) {
                        messageDiv.innerHTML = '<span class="access-locked">🔒 SYSTEM LOCKED</span>';
                        document.getElementById('passwordBtn').disabled = true;
                        passwordInput.disabled = true;
                        passwordInput.className = 'input-cyber error';
                        feedback.innerHTML = '<span class="text-red-400 text-xs">🔒 System locked. Please restart.</span>';
                        addLog('🔒 SYSTEM LOCKED - Maximum attempts exceeded', 'locked');
                        playErrorSound();
                        document.querySelector('.badge-cyber').innerHTML = `
                            <span class="dot-cyber locked"></span>
                            <span class="text-red-500 font-['Orbitron'] booting">🔴 SYSTEM LOCKED</span>
                        `;
                    }
                }
            } catch (error) {
                feedback.innerHTML = `<span class="text-red-400 text-xs">❌ Error: ${error.message}</span>`;
                playErrorSound();
            }
        }

        // === TIMESTAMP ===
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

        // === LOGS ===
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

        // === LOOKUP VEHICLE ===
        async function lookupVehicle() {
            const rc = document.getElementById('rcInput').value.trim();
            if (!rc) {
                addLog('❌ Please enter an RC number', 'error');
                playErrorSound();
                return;
            }

            document.getElementById('statusText').textContent = 'SEARCHING...';
            document.getElementById('statusText').style.color = '#60a5fa';
            document.getElementById('statusDot').className = 'dot-cyber active';
            playClickSound();
            addLog(`🔍 Searching for RC: ${rc}`, 'info');

            try {
                const response = await fetch('/lookup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rc: rc })
                });
                const data = await response.json();

                if (data.status === 'success') {
                    // Remove copyright fields from data
                    if (data.data && typeof data.data === 'object') {
                        // Filter out copyright fields
                        const filteredData = {};
                        for (const [key, value] of Object.entries(data.data)) {
                            // Skip any field containing "copyright", "COPYRIGHT", "source maker", "rajan", etc.
                            const keyLower = key.toLowerCase();
                            if (keyLower.includes('copyright') || 
                                keyLower.includes('source') || 
                                keyLower.includes('rajan') ||
                                keyLower.includes('maker') ||
                                keyLower.includes('credit') ||
                                keyLower.includes('@')) {
                                continue;
                            }
                            // Skip value if it contains copyright text
                            if (typeof value === 'string' && 
                                (value.toLowerCase().includes('copyright') || 
                                 value.toLowerCase().includes('rajan') ||
                                 value.toLowerCase().includes('source maker'))) {
                                continue;
                            }
                            filteredData[key] = value;
                        }
                        data.data = filteredData;
                    }
                    
                    currentData = data.data;
                    currentRc = rc;
                    displayResults(rc, data.data, data.cached, data.response_time);
                    addLog(`✅ Vehicle found for RC: ${rc}`, 'success');
                    playSuccessSound();
                    triggerSprinkles();
                    document.getElementById('statusText').textContent = 'SUCCESS';
                    document.getElementById('statusText').style.color = '#22c55e';
                    document.getElementById('statusDot').className = 'dot-cyber active';
                    document.getElementById('statusDot').style.background = '#22c55e';
                } else {
                    addLog(`❌ Error: ${data.message}`, 'error');
                    playErrorSound();
                    document.getElementById('statusText').textContent = 'ERROR';
                    document.getElementById('statusText').style.color = '#ef4444';
                    document.getElementById('statusDot').className = 'dot-cyber error';
                }
            } catch (error) {
                addLog(`❌ Request failed: ${error.message}`, 'error');
                playErrorSound();
                document.getElementById('statusText').textContent = 'ERROR';
                document.getElementById('statusText').style.color = '#ef4444';
                document.getElementById('statusDot').className = 'dot-cyber error';
            }
        }

        // === DISPLAY RESULTS ===
        function displayResults(rc, data, cached, responseTime) {
            document.getElementById('resultsSection').classList.remove('hidden');
            document.getElementById('apiStatusText').textContent = 'OK';
            document.getElementById('apiStatusText').style.color = '#22c55e';
            document.getElementById('cacheStatus').textContent = cached ? 'YES' : 'NO';
            document.getElementById('responseTime').textContent = responseTime || '--';

            const tbody = document.getElementById('resultsBody');
            tbody.innerHTML = '';
            
            // Fields to exclude (including copyright)
            const excludeFields = ['_api_time', 'cached', 'timestamp', 'copyright', 'COPYRIGHT', 'source_maker', 'credit'];
            
            let hasData = false;
            for (const [key, value] of Object.entries(data)) {
                // Skip excluded fields
                if (excludeFields.includes(key.toLowerCase())) continue;
                if (key.startsWith('_')) continue;
                
                // Skip if value is null/undefined/empty
                if (value === null || value === undefined || value === '') continue;
                
                // Skip if value contains copyright text
                if (typeof value === 'string' && 
                    (value.toLowerCase().includes('copyright') || 
                     value.toLowerCase().includes('rajan') ||
                     value.toLowerCase().includes('source maker'))) {
                    continue;
                }
                
                hasData = true;
                const tr = document.createElement('tr');
                const displayKey = key.replace(/_/g, ' ').toUpperCase();
                tr.innerHTML = `
                    <td class="field">${displayKey}</td>
                    <td class="value">${typeof value === 'object' ? JSON.stringify(value) : value}</td>
                `;
                tbody.appendChild(tr);
            }

            if (!hasData) {
                tbody.innerHTML = `<tr><td colspan="2" class="text-center text-gray-500 py-8">No vehicle data found</td></tr>`;
            }
        }

        // === CLEAR RESULTS ===
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
            playClickSound();
        }

        // === EXPORT RESULT ===
        function exportResult() {
            if (!currentData) {
                alert('No data to export. Please lookup a vehicle first.');
                playErrorSound();
                return;
            }
            
            // Remove copyright fields before export
            const cleanData = {};
            for (const [key, value] of Object.entries(currentData)) {
                if (key.toLowerCase().includes('copyright') || 
                    key.toLowerCase().includes('source') || 
                    key.toLowerCase().includes('rajan') ||
                    key.toLowerCase().includes('maker')) {
                    continue;
                }
                if (typeof value === 'string' && 
                    (value.toLowerCase().includes('copyright') || 
                     value.toLowerCase().includes('rajan'))) {
                    continue;
                }
                cleanData[key] = value;
            }
            
            const data = {
                rc: currentRc,
                timestamp: new Date().toISOString(),
                data: cleanData
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `vehicle_${currentRc}_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
            addLog(`📥 Exported data for ${currentRc}`, 'success');
            playSuccessSound();
        }

        // === COPY RESULT ===
        function copyResult() {
            if (!currentData) {
                alert('No data to copy. Please lookup a vehicle first.');
                playErrorSound();
                return;
            }
            
            // Remove copyright fields before copy
            const cleanData = {};
            for (const [key, value] of Object.entries(currentData)) {
                if (key.toLowerCase().includes('copyright') || 
                    key.toLowerCase().includes('source') || 
                    key.toLowerCase().includes('rajan') ||
                    key.toLowerCase().includes('maker')) {
                    continue;
                }
                if (typeof value === 'string' && 
                    (value.toLowerCase().includes('copyright') || 
                     value.toLowerCase().includes('rajan'))) {
                    continue;
                }
                cleanData[key] = value;
            }
            
            const text = JSON.stringify(cleanData, null, 2);
            navigator.clipboard.writeText(text).then(() => {
                addLog(`📋 Copied data for ${currentRc} to clipboard`, 'success');
                playSuccessSound();
                const btn = document.getElementById('copyBtn');
                const originalText = btn.textContent;
                btn.textContent = '✅ COPIED!';
                setTimeout(() => { btn.textContent = originalText; }, 2000);
            }).catch(() => {
                addLog('❌ Failed to copy data', 'error');
                playErrorSound();
            });
        }

        // === INIT ===
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('passwordInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    verifyPassword();
                }
            });
            document.getElementById('rcInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    lookupVehicle();
                }
            });
            addLog('🟢 Vehicle Lookup System ready', 'info');
            addLog('🔐 Enter password to unlock', 'info');
            setTimeout(() => {
                showBooting();
            }, 500);
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
        
        cached_data = load_cache(rc)
        if cached_data:
            return {
                "status": "success",
                "data": cached_data,
                "cached": True,
                "response_time": 0
            }
        
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
