from analysis.prereg import fisher_one_sided, trend_one_sided


def test_fisher_against_scipy_values():
    # reference values computed with scipy.stats.fisher_exact(alternative="greater")
    assert abs(fisher_one_sided(8, 20, 1, 20) - 0.0099) < 5e-4
    assert abs(fisher_one_sided(5, 20, 1, 20) - 0.0908) < 5e-4
    assert fisher_one_sided(0, 20, 0, 20) == 1.0
    assert abs(fisher_one_sided(20, 20, 0, 20) - 7.25e-12) < 1e-12


def test_trend_edges_and_direction():
    assert trend_one_sided([(0, 20)] * 5) == 1.0
    assert trend_one_sided([(20, 20)] * 5) == 1.0
    up = trend_one_sided([(0, 20), (1, 20), (3, 20), (6, 20), (10, 20)])
    down = trend_one_sided([(10, 20), (6, 20), (3, 20), (1, 20), (0, 20)])
    assert up < 0.001 and down > 0.999
