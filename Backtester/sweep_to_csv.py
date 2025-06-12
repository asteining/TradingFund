import os
import json
import pandas as pd


def load_sweep_results(sweep_dir: str) -> pd.DataFrame:
    """Load all JSON P&L files from sweep_dir and return summary DataFrame."""
    records = []
    for fname in os.listdir(sweep_dir):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(sweep_dir, fname)
        with open(path, 'r') as f:
            data = json.load(f)
        # parse parameters from filename: pnl_{period}_{devfactor}_{stake}.json
        base = os.path.splitext(fname)[0]
        try:
            _, period, devfactor, stake = base.split('_')
            period = int(period)
            devfactor = float(devfactor)
            stake = int(stake)
        except ValueError:
            # unexpected filename format
            period = devfactor = stake = None
        pnl = data[-1]['value'] if data else 0
        records.append({
            'period': period,
            'devfactor': devfactor,
            'stake': stake,
            'final_pnl': pnl,
        })
    return pd.DataFrame(records)


def main() -> None:
    sweep_dir = os.path.join(os.path.dirname(__file__), '..', 'API', 'pnl_sweep')
    df = load_sweep_results(sweep_dir)
    output_path = os.path.join(os.path.dirname(__file__), '..', 'API', 'sweep_summary.csv')
    df.to_csv(output_path, index=False)
    print("Wrote ../API/sweep_summary.csv")


if __name__ == '__main__':
    main()
