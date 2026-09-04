from pathlib import Path
import pandas as pd
from biodiversity_engine import validate_observations, validate_habitats, calculate_observation_risk, habitat_summary

ROOT = Path(__file__).resolve().parent
obs = pd.read_csv(ROOT/'data/sample_observations.csv')
hab = pd.read_csv(ROOT/'data/sample_habitats.csv')
obs_err = validate_observations(obs)
hab_err = validate_habitats(hab)
assert not obs_err, obs_err
assert not hab_err, hab_err
scored = calculate_observation_risk(obs)
hs = habitat_summary(hab)
assert scored['attention_score'].between(0,100).all()
assert scored['risk_band'].notna().all()
assert hs['biodiversity_support_score'].between(0,100).all()
assert obs['observation_id'].is_unique
assert hab['habitat_id'].is_unique
print('PASS: UrbanBioTrack biodiversity observation screening')
print(f'Observations {len(obs)} | Species {obs.species_common_name.nunique()} | Habitats {len(hab)}')
print(f'Attention range {scored.attention_score.min():.1f}–{scored.attention_score.max():.1f} | High/Critical {int(scored.risk_band.astype(str).isin(["High","Critical"]).sum())}')
print('Schema, scoring, range, and uniqueness checks passed')
