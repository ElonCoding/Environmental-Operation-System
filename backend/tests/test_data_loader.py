import pytest
from backend.app.services.data_loader import data_loader, CANONICAL_GHATS

def test_dataset_loading_and_counts():
    df = data_loader.get_df()
    assert len(df) == 1524
    assert set(df['year'].unique()) == {2023, 2024, 2025}
    assert set(df['festival'].unique()) == {"Ganesh", "Durga"}
    assert set(df['phase'].unique()) == {"pre", "during", "after"}
    assert len(df['parameter'].unique()) == 13

def test_seven_standardised_ghats():
    df = data_loader.get_df()
    unique_sites = set(df['site'].unique())
    assert len(unique_sites) == 7
    for site_name in CANONICAL_GHATS:
        assert site_name in unique_sites

def test_site_match_confidence_integrity():
    df = data_loader.get_df()
    # Rani Kamlapati must have medium confidence
    rk = df[df['site'] == "Rani Kamlapati ghat / Kamla Park kund"]
    assert (rk['site_match_confidence'] == "medium").all()

    # Others must have high confidence
    for other_site in ["Khatlapura ghat", "Prempura ghat", "Bairagarh (Sant Hirdaram) kund"]:
        sub = df[df['site'] == other_site]
        assert (sub['site_match_confidence'] == "high").all()

def test_source_page_and_report_provenance():
    df = data_loader.get_df()
    assert df['source_page'].notna().all()
    assert (df['source_page'] > 0).all()
    assert df['report_filename'].str.endswith('.pdf').all()

    # 2023 -> Idol_immer._Report_23_CPCB.pdf
    sub_23 = df[df['year'] == 2023]
    assert (sub_23['report_filename'] == "Idol_immer._Report_23_CPCB.pdf").all()

    # 2024 -> Ganesh_and_Durga_visarjan_report-2024.pdf
    sub_24 = df[df['year'] == 2024]
    assert (sub_24['report_filename'] == "Ganesh_and_Durga_visarjan_report-2024.pdf").all()

    # 2025 -> Ganesh_and_Durga_visarjan_report-2025.pdf
    sub_25 = df[df['year'] == 2025]
    assert (sub_25['report_filename'] == "Ganesh_and_Durga_visarjan_report-2025.pdf").all()
