"""
MUCAMBO Nexus - Main Entrypoint
Starts the 24/7 Autonomous Intangible Asset Arbitrage Server and Control Dashboard.
"""

import sys
import uvicorn
from config import HOST, PORT

BANNER = r"""
==============================================================================
   __  _____  ___________   __  ______  ____     _   _________  ____  ______
  /  |/  / / / / ____/   | /  |/  / __ )/ __ \   / | / / ____/ |/ / / / / ___/
 / /|_/ / / / / /   / /| |/ /|_/ / __  / / / /  /  |/ / __/  |   / / / /\__ \ 
/ /  / / /_/ / /___/ ___ / /  / / /_/ / /_/ /  / /|  / /___ /   / /_/ /___/ / 
/_/  /_/\____/\____/_/  |_/_/  /_/_____/\____/  /_/ |_/_____//_/|_|\____//____/  
==============================================================================
   AUTONOMOUS 24/7 INTANGIBLE ASSET ARBITRAGE & JUST-IN-TIME LIQUIDATION ENGINE
   Zero-Inventory | Real-Time Multi-Asset Scanner | Adaptive i18n & Currencies
==============================================================================
"""

def main():
    import os
    runtime_port = int(os.getenv("PORT", str(PORT)))
    runtime_host = os.getenv("HOST", "0.0.0.0")

    print(BANNER)
    print(f"[*] Starting MUCAMBO Nexus on http://{runtime_host}:{runtime_port}")
    print(f"[*] Access the Dashboard in your browser: http://localhost:{runtime_port}")
    print(f"[*] Press CTRL+C to terminate cleanly.\n")

    uvicorn.run(
        "web.app:app",
        host=runtime_host,
        port=runtime_port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
