from pathlib import Path
import pandas as pd
from biodiversity_engine import calculate_observation_risk, habitat_summary, species_summary, monthly_trend, validate_observations, validate_habitats

ROOT = Path(__file__).resolve().parents[1]

def test_observation_schema():
    df = pd.read_csv(ROOT/'data/sample_observations.csv')
    assert validate_observations(df) == []

def test_habitat_schema():
    df = pd.read_csv(ROOT/'data/sample_habitats.csv')
    assert validate_habitats(df) == []

def test_score_bounds_and_band():
    df = calculate_observation_risk(pd.read_csv(ROOT/'data/sample_observations.csv'))
    assert df.attention_score.between(0,100).all()
    assert df.risk_band.notna().all()

def test_species_and_trend():
    df = calculate_observation_risk(pd.read_csv(ROOT/'data/sample_observations.csv'))
    assert len(species_summary(df)) >= 5
    assert not monthly_trend(df).empty

def test_habitat_metrics():
    h = habitat_summary(pd.read_csv(ROOT/'data/sample_habitats.csv'))
    assert h.biodiversity_support_score.between(0,100).all()
