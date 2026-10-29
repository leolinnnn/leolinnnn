"""Analytical edge cases for selected original Bang Na functions."""
import math
import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.network_metrics import nearest_node, nearest_reachable_node, segment_circle_inside_length, buffer_road_context
from src.poi_diversity import shannon_evenness, buffer_function_context
from src.regression import ols_fit
from src.segmentation_metrics import ratios_for_mask, aggregate_results


class KernelTests(unittest.TestCase):
    def test_scene_crop_keeps_vegetation_and_terrain_distinct(self):
        mask = np.full((640, 640), 8, dtype=np.uint8)
        mask[-40:] = 9
        values = ratios_for_mask(mask, 40)
        self.assertEqual(values["gvi_vegetation_scene"], 1)
        self.assertAlmostEqual(values["gvi_vegetation_full"], 600/640)
        self.assertEqual(values["gvi_vegetation_terrain_full"], 1)
        self.assertEqual(values["terrain_scene"], 0)

    def test_aggregation_uses_point_then_area_means(self):
        rows = []
        for i, (point, value) in enumerate([("p1", .1), ("p1", .2), ("p1", .3), ("p1", .4), ("p2", .9)]):
            mask = np.array([[8, 9], [0, 0]], dtype=np.uint8)
            row = ratios_for_mask(mask, 0)
            row.update(candidate_id=point, area_id="A01", res_type="A", type_name="Condo", lat=0, lon=0, heading=i*90)
            row["gvi_vegetation_scene"] = value
            rows.append(row)
        points, areas, _ = aggregate_results(pd.DataFrame(rows))
        self.assertEqual(len(points), 2)
        self.assertAlmostEqual(areas.gvi_vegetation_scene_mean.iloc[0], .575)

    def test_hc3_intercept_only_closed_form(self):
        fit = ols_fit(pd.DataFrame({"Intercept": [1.] * 4}), pd.Series([1., 2., 3., 4.]))
        self.assertAlmostEqual(fit["beta"][0], 2.5)
        self.assertAlmostEqual(fit["se_hc3"][0], math.sqrt(5) / 3)
        self.assertEqual(fit["df_resid"], 3)

    def test_routing_fallback_and_buffer_boundary(self):
        coords = {"disconnected": (0., 0.), "reachable": (3., 4.)}
        self.assertEqual(nearest_node(0, 0, coords), ("disconnected", 0.))
        self.assertEqual(nearest_reachable_node(0, 0, coords, {"reachable"}), ("reachable", 5.))
        self.assertAlmostEqual(segment_circle_inside_length(-2, 0, 2, 0, 0, 0, 1), 2.)
        self.assertEqual(segment_circle_inside_length(-2, 1, 2, 1, 0, 0, 1), 0.)
        segments = [{"ax": -2, "ay": 0, "bx": 2, "by": 0, "hierarchy_score": 3, "road_class": "major"}]
        result = buffer_road_context(0, 0, 1, segments, [{"x": 0, "y": 0, "degree": 3}])
        self.assertEqual(result["major_road_share_1m"], 1.)
        self.assertEqual(result["intersection_count_1m"], 1)

    def test_poi_entropy_and_circle_inclusion(self):
        entropy, evenness, active = shannon_evenness([2, 2, 0])
        self.assertAlmostEqual(entropy, math.log(2))
        self.assertEqual((evenness, active), (1., 2))
        self.assertEqual(shannon_evenness([0, 0]), (0., 0., 0))
        pois = [{"x": 0, "y": 0, "functional_category": "retail"},
                {"x": 400, "y": 0, "functional_category": "education"},
                {"x": 401, "y": 0, "functional_category": "retail"}]
        result = buffer_function_context(0, 0, 400, pois)
        self.assertEqual(result["poi_count_400m"], 2)
        self.assertAlmostEqual(result["poi_shannon_400m"], math.log(2))


if __name__ == "__main__":
    unittest.main()
