import os
import subprocess
from itertools import product

periods = [10, 20, 30]
devfactors = [1.5, 2.0, 2.5]
stakes = [50, 100, 200]

# Output directory relative to this script
output_dir = os.path.join('..', 'API', 'pnl_sweep')
os.makedirs(output_dir, exist_ok=True)

for period, devfactor, stake in product(periods, devfactors, stakes):
    output_path = os.path.join(output_dir, f'pnl_{period}_{devfactor}_{stake}.json')
    cmd = [
        'python', 'backtest.py',
        '--symbol', 'CRYPTO_BTCUSD',
        '--start', '2015-06-09',
        '--end', '2025-06-09',
        '--cash', '100000',
        '--period', str(period),
        '--devfactor', str(devfactor),
        '--stake', str(stake),
        '--strategy', 'mean_reversion',
        '--output', output_path,
    ]
    print(f'Running: {" ".join(cmd)}')
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")

