from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

OBS_REQUIRED = [
    'observation_id','observed_at','species_common_name','species_category','habitat_type',
    'observer_id','latitude','longitude','image_count','abundance_count','season',
    'habitat_quality_score','human_disturbance_score','species_confidence_pct'
]
HAB_REQUIRED = [
    'habitat_id','habitat_name','habitat_type','zone','area_hectares','native_plant_pct',
    'canopy_cover_pct','water_availability_score','fragmentation_score','disturbance_score','seasonal_stability_score'
]

CATEGORIES = ['Birds','Insects','Plants','Mammals','Reptiles','Amphibians','Other']

@dataclass(frozen=True)
class ScoreWeights:
    observation_quality: float = 0.18
    habitat_pressure: float = 0.18
    disturbance: float = 0.18
    diversity_signal: float = 0.20
    seasonal_change: float = 0.16
    confidence: float = 0.10


def _norm(s: pd.Series, lo: float, hi: float) -> pd.Series:
    return ((s.astype(float) - lo) / (hi - lo)).clip(0,1)


def validate_observations(df: pd.DataFrame) -> list[str]:
    missing = [c for c in OBS_REQUIRED if c not in df.columns]
    errors = []
    if missing:
        errors.append(f"Observations CSV is missing required column(s): {', '.join(missing)}")
        return errors
    if df.empty:
        errors.append('Observations CSV contains no rows.')
    if df['observation_id'].duplicated().any():
        errors.append('observation_id must be unique.')
    for c in ['image_count','abundance_count','habitat_quality_score','human_disturbance_score','species_confidence_pct','latitude','longitude']:
        if not pd.api.types.is_numeric_dtype(df[c]):
            errors.append(f'{c} must be numeric.')
    if not df['species_common_name'].astype(str).str.strip().all():
        errors.append('species_common_name contains blank values.')
    return errors


def validate_habitats(df: pd.DataFrame) -> list[str]:
    missing = [c for c in HAB_REQUIRED if c not in df.columns]
    errors = []
    if missing:
        errors.append(f"Habitat CSV is missing required column(s): {', '.join(missing)}")
        return errors
    if df.empty:
        errors.append('Habitat CSV contains no rows.')
    if df['habitat_id'].duplicated().any():
        errors.append('habitat_id must be unique.')
    return errors


def prepare_observations(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out['observed_at'] = pd.to_datetime(out['observed_at'], errors='coerce')
    numeric = ['latitude','longitude','image_count','abundance_count','habitat_quality_score','human_disturbance_score','species_confidence_pct']
    for c in numeric:
        out[c] = pd.to_numeric(out[c], errors='coerce')
    out['season'] = out['season'].fillna('Unknown').astype(str)
    out['species_category'] = out['species_category'].fillna('Other').astype(str)
    return out


def calculate_observation_risk(df: pd.DataFrame, weights: ScoreWeights = ScoreWeights()) -> pd.DataFrame:
    out = prepare_observations(df)
    abundance_norm = _norm(out['abundance_count'].fillna(1), 1, max(float(out['abundance_count'].max()), 2))
    quality = _norm(out['habitat_quality_score'].fillna(50), 0, 100)
    disturbance = _norm(out['human_disturbance_score'].fillna(50), 0, 100)
    confidence = _norm(out['species_confidence_pct'].fillna(70), 0, 100)
    # Higher score = higher attention need, not ecological value.
    diversity_signal = 1 - abundance_norm
    habitat_pressure = 1 - quality
    seasonal_change = 0.5
    score = 100*(
        weights.observation_quality*(1-quality) +
        weights.habitat_pressure*habitat_pressure +
        weights.disturbance*disturbance +
        weights.diversity_signal*diversity_signal +
        weights.seasonal_change*seasonal_change +
        weights.confidence*(1-confidence)
    )
    out['attention_score'] = score.clip(0,100).round(1)
    out['risk_band'] = pd.cut(out['attention_score'], [-0.01,24.9,49.9,74.9,100.1], labels=['Low','Moderate','High','Critical'])
    out['attention_driver'] = np.select(
        [disturbance >= 0.72, habitat_pressure >= 0.62, confidence <= 0.55, abundance_norm <= 0.25],
        ['Human disturbance','Habitat pressure','Low observation confidence','Low observed abundance'],
        default='Mixed signals'
    )
    return out


def species_summary(obs: pd.DataFrame) -> pd.DataFrame:
    g = obs.groupby(['species_common_name','species_category'], dropna=False).agg(
        observations=('observation_id','count'),
        total_abundance=('abundance_count','sum'),
        avg_confidence=('species_confidence_pct','mean'),
        avg_habitat_quality=('habitat_quality_score','mean'),
        avg_disturbance=('human_disturbance_score','mean'),
    ).reset_index()
    g['attention_score'] = (
        100*(0.38*(1-g['avg_habitat_quality']/100)+0.34*g['avg_disturbance']/100+0.28*(1-g['avg_confidence']/100))
    ).clip(0,100).round(1)
    g['attention_band'] = pd.cut(g['attention_score'], [-.01,24.9,49.9,74.9,100], labels=['Low','Moderate','High','Critical'])
    return g.sort_values(['observations','total_abundance'], ascending=False)


def monthly_trend(obs: pd.DataFrame) -> pd.DataFrame:
    d = obs.dropna(subset=['observed_at']).copy()
    d['month'] = d['observed_at'].dt.to_period('M').dt.to_timestamp()
    return d.groupby(['month','species_category']).size().reset_index(name='observations').sort_values('month')


def habitat_summary(hab: pd.DataFrame) -> pd.DataFrame:
    d = hab.copy()
    for c in HAB_REQUIRED[4:]:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    d['biodiversity_support_score'] = (
        0.28*d['native_plant_pct'] +
        0.22*d['canopy_cover_pct'] +
        0.18*d['water_availability_score'] +
        0.18*d['seasonal_stability_score'] +
        0.14*(100-d['fragmentation_score'])
    ).clip(0,100).round(1)
    d['pressure_score'] = (0.45*d['disturbance_score'] + 0.35*d['fragmentation_score'] + 0.20*(100-d['seasonal_stability_score'])).clip(0,100).round(1)
    return d


def biodiversity_kpis(obs: pd.DataFrame, hab: pd.DataFrame) -> dict:
    species = obs['species_common_name'].nunique()
    observations = len(obs)
    habitats = hab['habitat_id'].nunique()
    contributors = obs['observer_id'].nunique()
    images = int(obs['image_count'].fillna(0).sum())
    avg_conf = float(obs['species_confidence_pct'].mean()) if len(obs) else 0
    return {
        'observations': observations, 'species': species, 'habitats': habitats,
        'contributors': contributors, 'images': images, 'avg_confidence': avg_conf
    }


def scenario_projection(obs: pd.DataFrame, disturbance_delta: float, habitat_delta: float, confidence_delta: float) -> dict:
    base = calculate_observation_risk(obs)['attention_score'].mean()
    projected = np.clip(base + disturbance_delta*0.42 - habitat_delta*0.36 - confidence_delta*0.18, 0, 100)
    def band(v):
        return 'Low' if v < 25 else 'Moderate' if v < 50 else 'High' if v < 75 else 'Critical'
    return {'baseline': round(float(base),1), 'projected': round(float(projected),1), 'band': band(projected)}
