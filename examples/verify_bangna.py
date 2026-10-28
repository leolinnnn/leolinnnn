"""Recompute Bang Na's area-level findings from the included 25-area table.

This portable example is prepared for the portfolio from the existing research
outputs. It does not repeat street-view inference or manual interface coding.
Requires Python 3.10+, numpy, pandas and scipy. Run from any working directory.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats


def fit_model(area, with_interface=True):
    columns = ['network_dist_to_bts_mean_m', 'major_road_share_in_polygon',
               'poi_shannon_400m_mean']
    if with_interface:
        columns.insert(0, 'interface_openness_mean')
    z = (area[columns] - area[columns].mean()) / area[columns].std(ddof=1)
    # Shophouse (C) is the reference type; continuous predictors are z-scored.
    x = np.column_stack([np.ones(len(area)),
                         *[area.res_type.eq(t).astype(float) for t in 'ABD'], z])
    y = area.gvi_pct.to_numpy()
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    n, k = x.shape
    r2 = 1 - np.sum(residual**2) / np.sum((y-y.mean())**2)
    bread = np.linalg.inv(x.T @ x)
    leverage = np.einsum('ij,jk,ik->i', x, bread, x)
    scale = (residual / (1-leverage))**2
    covariance = bread @ (x.T @ (x * scale[:, None])) @ bread
    se = np.sqrt(np.diag(covariance))
    result = {'n_areas': n, 'adjusted_r_squared': float(1-(1-r2)*(n-1)/(n-k))}
    if with_interface:
        margin = stats.t.ppf(.975, n-k) * se[4]
        result.update({'io_pp_per_sd': float(beta[4]),
                       'io_hc3_ci95': [float(beta[4]-margin), float(beta[4]+margin)],
                       'io_p': float(2*stats.t.sf(abs(beta[4]/se[4]),n-k))})
    return result


def main():
    area = pd.read_csv(Path(__file__).resolve().parent/'data/bangna-areas.csv')
    if len(area) != 25 or area.area_id.nunique() != 25:
        raise ValueError('Expected 25 unique residential areas')
    h, p = stats.kruskal(*[area.loc[area.res_type.eq(t),'gvi_pct'] for t in 'ABCD'])
    rho, rho_p = stats.spearmanr(area.interface_openness_mean, area.gvi_pct)
    return {'n_gvi_points': int(area.gvi_point_count.sum()),
            'n_images': int(area.n_images.sum()),
            'kruskal_h': float(h), 'kruskal_p': float(p),
            'io_gvi_spearman': float(rho), 'spearman_p': float(rho_p),
            'M2': fit_model(area,False), 'M2-I': fit_model(area,True)}


if __name__ == '__main__':
    print(json.dumps(main(),indent=2))
