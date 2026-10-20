# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""Software identity and bibliography shared by published data and reports."""

SOFTWARE_NAME = "Coarse-Graining Genesis Framework V5.0"
SOFTWARE_VERSION = "5.0.2"

BIBLIOGRAPHY = (
    ("2026a", "Certified Spectral Computation for Semilinear Evolution: Finite Records and Polynomial Bit Cost"),
    ("2026b", "Coarse-Graining and Long-Range Response in Generated Systems"),
    ("2026c", "Dynamics of Generated Spectra from Minimal Change: Certified Function Classes and Finite Windows"),
    ("2026d", "The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap"),
    ("2026e", "A Spectral Construction of Natural-Number Arithmetic"),
    ("2026f", "A Spectral Criterion for Emergent Gravity"),
    ("2026g", "The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales"),
    ("2026h", "The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation"),
)

PUBLICATION_NOTICE = (
    SOFTWARE_NAME,
    "Author: Jinku Guo <guojk@nwpu.edu.cn>",
    "Northwestern Polytechnical University, Xi'an 710072, China",
    "ORCID: 0009-0000-6600-6171",
    "References:",
    *(f"Guo, J. ({year}). {title}. Unpublished manuscript."
      for year, title in BIBLIOGRAPHY),
    "Full bibliography: REFERENCES.md and CITATION.cff.",
)


def publication_metadata() -> dict:
    """Return an independent JSON-compatible description of this software."""
    return {
        "software": SOFTWARE_NAME,
        "version": SOFTWARE_VERSION,
        "author": "Jinku Guo",
        "references": [
            {"citation": f"Guo ({year})", "title": title,
             "author": "Jinku Guo", "year": 2026,
             "status": "unpublished manuscript"}
            for year, title in BIBLIOGRAPHY
        ],
    }
