from src.analyzer import analyze_program
from src.demo_extractor import extract_program_data

def test_project_phoenix_detects_watermelon():
    data = extract_program_data("demo")
    result = analyze_program(data)
    assert result["reported_status"] == "GREEN"
    assert result["watermelon"] is True
    assert result["assessed_status"] in {"YELLOW", "RED"}

def test_performance_gap_is_detected():
    data = extract_program_data("demo")
    result = analyze_program(data)
    metric = result["metric_results"][0]
    assert metric["below_target"] is True
    assert metric["gap_pct"] == 12.0

def test_dependency_compression_is_detected():
    data = extract_program_data("demo")
    result = analyze_program(data)
    assert len(result["dependency_warnings"]) >= 1
