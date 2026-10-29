"""Array kernel lifted from rebuild_native_c2_ndvi.py main(); see ../PROVENANCE.md."""
import numpy as np

def compute_ndvi(arrays):
    """Return NDVI and three QA masks for aligned Landsat 8 C2 L2 arrays.

    Keys: SR_B4, SR_B5, QA_PIXEL, QA_RADSAT, SR_QA_AEROSOL.
    Use the original 2021-09-07 scene; no resampling occurs here.
    """
    shapes = {np.asarray(value).shape for value in arrays.values()}
    if len(shapes) != 1:
        raise ValueError("All five source arrays must have the same shape")
    coeff = {4: (2.75e-05, -0.2), 5: (2.75e-05, -0.2)}
    red_dn = arrays["SR_B4"]
    nir_dn = arrays["SR_B5"]
    qa = arrays["QA_PIXEL"]
    sat = arrays["QA_RADSAT"]
    aer = arrays["SR_QA_AEROSOL"]
    red = red_dn.astype(np.float64) * coeff[4][0] + coeff[4][1]
    nir = nir_dn.astype(np.float64) * coeff[5][0] + coeff[5][1]
    spectral = ((red_dn > 0) & (nir_dn > 0) &
                (red > 0) & (nir > 0) & (red <= 1) & (nir <= 1) &
                ((red + nir) > 0))
    qa_clear_common = (qa & sum(1 << bit for bit in range(6))) == 0
    qa_land = (qa & (1 << 7)) == 0
    no_sat = (sat & ((1 << 3) | (1 << 4) | (1 << 11))) == 0
    aer_not_fill = (aer & 1) == 0
    aer_not_high = ((aer >> 6) & 3) != 3
    common = spectral & qa_clear_common & no_sat & aer_not_fill
    valid = {
        "primary": common & qa_land & aer_not_high,
        "include_water": common & aer_not_high,
        "include_high_aerosol": common & qa_land,
    }
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red)
    if np.any((ndvi[valid["primary"]] < -1) | (ndvi[valid["primary"]] > 1)):
        raise AssertionError("Primary NDVI outside [-1,1]")
    return ndvi, valid
