"""Boundary checks for the published research kernels; synthetic fixtures only."""
import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ndvi_aggregation import summarize_polygon
from src.ndvi_reflectance import compute_ndvi
from src.road_aggregation import choose_unique_content, segment_aggregate
from src.spatial_statistics import pearson_from_moments


class KernelTests(unittest.TestCase):
    def test_reflectance_offset_and_qa_variants(self):
        arrays = {"SR_B4": np.full((1, 6), 10000, dtype=np.uint16),
                  "SR_B5": np.full((1, 6), 20000, dtype=np.uint16),
                  "QA_PIXEL": np.array([[0, 128, 8, 0, 0, 0]], dtype=np.uint16),
                  "QA_RADSAT": np.array([[0, 0, 0, 8, 0, 0]], dtype=np.uint16),
                  "SR_QA_AEROSOL": np.array([[0, 0, 0, 0, 192, 1]], dtype=np.uint8)}
        ndvi, masks = compute_ndvi(arrays)
        self.assertAlmostEqual(ndvi[0, 0], .275 / .425)
        self.assertNotAlmostEqual(ndvi[0, 0], 1 / 3)  # raw DN ratio is not SR NDVI
        self.assertEqual(masks["primary"].tolist(), [[True, False, False, False, False, False]])
        self.assertEqual(masks["include_water"].tolist(), [[True, True, False, False, False, False]])
        self.assertEqual(masks["include_high_aerosol"].tolist(), [[True, False, False, False, True, False]])

    def test_area_weights_and_missing_pixels(self):
        polygon = shapely.box(0, 0, 45, 30)
        grid = (0, 30, 0, 30, 0, -30)
        data = {"primary": np.array([[.2, .8]]), "masked": np.array([[.2, np.nan]])}
        result = summarize_polygon(polygon, data, grid, 2, 1, tuple(data))
        self.assertAlmostEqual(result["primary"][0], .4)  # 900*.2 + 450*.8 over 1350
        self.assertAlmostEqual(result["primary"][1], 1)
        self.assertAlmostEqual(result["masked"][0], .2)
        self.assertAlmostEqual(result["masked"][1], 2 / 3)
        self.assertLess(result["masked"][1], .8)

    def test_road_deduplication_excludes_ambiguous_matches(self):
        entries = [("a", "a1", "r1", 1, 1, .4), ("a", "a2", "r1", 2, 1, .4),
                   ("b", "b1", "r1", 3, 1, .8), ("c", "c1", "r1", 1, 1, .9),
                   ("c", "c2", "r2", 1, 1, .9), ("tie", "t", "r1", 1, 2, .9),
                   ("far", "f", "r1", 26, 1, .9)]
        frame = pd.DataFrame(entries, columns=["content_id_sha256", "image_id", "nearest_segment_id",
                            "nearest_osm_road_distance_m", "nearest_tie_count", "gvi_vt_existing"])
        frame["capture_year_month"] = "2021-09"
        frame["nearest_highway"] = "residential"
        frame["nearest_osm_way_id"] = "w1"
        selected, _ = choose_unique_content(frame, 25)
        self.assertEqual(selected.image_id.tolist(), ["a1", "b1"])
        roads = pd.DataFrame({"segment_id": ["r1", "r2"], "length_m": [100., 200.]})
        result, _ = segment_aggregate(roads, selected, 25)
        self.assertEqual(result.panorama_n.tolist(), [2, 0])
        self.assertAlmostEqual(result.gvi_vt_mean.iloc[0], .6)
        self.assertTrue(pd.isna(result.gvi_vt_mean.iloc[1]))

    def test_moment_correlation_including_zero_variance(self):
        x = np.array([1., 2., 5., 7.])
        y = np.array([8., 3., 4., 2.])
        moments = np.array([[len(x), x.sum(), (x*x).sum(), y.sum(), (y*y).sum(), (x*y).sum()],
                            [4, 4, 4, 4, 4, 4]], dtype=float)
        result = pearson_from_moments(moments)
        self.assertAlmostEqual(result[0], np.corrcoef(x, y)[0, 1])
        self.assertTrue(np.isnan(result[1]))


if __name__ == "__main__":
    unittest.main()
