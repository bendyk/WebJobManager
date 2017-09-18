cwlVersion: v1.0
class: Workflow

inputs:
  ex_fits_tbl:  string
  ex_BM_factor: string
  ex_corr_tbl:  string
  ex_mosaic:    string
  ex_shrunken:  string
  ex_jpeg:      string

  ex_statfile: File
  ex_pimages:  File
  ex_cimages:  File
  ex_hdr:      File

  2mass_1: File
  2mass_2: File
  2mass_3: File
  2mass_4: File

  2mass_area_1: string
  2mass_area_2: string
  2mass_area_3: string
  2mass_area_4: string

  2mass_factor_1: string
  2mass_factor_2: string
  2mass_factor_3: string
  2mass_factor_4: string

  diff_1:  string
  diff_2:  string
  diff_3:  string
  diff_4:  string
  diff_5:  string

  fit_txt_1: string
  fit_txt_2: string
  fit_txt_3: string
  fit_txt_4: string
  fit_txt_5: string
  
outputs:
  outo: string


steps:
  mProjectPP1:
    run: mProjectPP.cwl
    in:
      factor: 2mass_factor_1
      2mass:
        source: 2mass_1
      hdr:
        source: ex_hdr
      2mass_area_out: 2mass_area_1
    out:
      [p2mass, p2mass_area]

  mProjectPP2:
    run: mProjectPP.cwl
    in:
      factor: 2mass_factor_2
      2mass:
        source: 2mass_2
      hdr:
        source: ex_hdr
      2mass_area_out: 2mass_area_2
    out:
      [p2mass, p2mass_area]

  mProjectPP3:
    run: mProjectPP.cwl
    in:
      factor: 2mass_factor_3
      2mass:
        source: 2mass_3
      hdr:
        source: ex_hdr
      2mass_area_out: 2mass_area_3
    out:
      [p2mass, p2mass_area]

  mProjectPP4:
    run: mProjectPP.cwl
    in:
      factor: 2mass_factor_4
      2mass:
        source: 2mass_4
      hdr:
        source: ex_hdr
      2mass_area_out: 2mass_area_4
    out:
      [p2mass, p2mass_area]

  mDiff1:
    run: mDiff.cwl
    in:
      p2mass1:
        source: mProjectPP1/p2mass
      p2mass2:
        source: mProjectPP2/p2mass
      p2mass1_area:
        source: mProjectPP1/p2mass_area
      p2mass2_area:
        source: mProjectPP2/p2mass_area
      diff: diff_1
      hdr:
        source: ex_hdr
    out:
      [diff_out]


  mDiff2:
    run: mDiff.cwl
    in:
      p2mass1:
        source: mProjectPP3/p2mass
      p2mass2:
        source: mProjectPP1/p2mass
      p2mass1_area:
        source: mProjectPP3/p2mass_area
      p2mass2_area:
        source: mProjectPP1/p2mass_area
      diff: diff_2
      hdr:
        source: ex_hdr
    out:
      [diff_out]

  mDiff3:
    run: mDiff.cwl
    in:
      p2mass1:
        source: mProjectPP3/p2mass
      p2mass2:
        source: mProjectPP2/p2mass
      p2mass1_area:
        source: mProjectPP3/p2mass_area
      p2mass2_area:
        source: mProjectPP2/p2mass_area
      diff: diff_3
      hdr:
        source: ex_hdr
    out:
      [diff_out]


  mDiff4:
    run: mDiff.cwl
    in:
      p2mass1:
        source: mProjectPP4/p2mass
      p2mass2:
        source: mProjectPP2/p2mass
      p2mass1_area:
        source: mProjectPP4/p2mass_area
      p2mass2_area:
        source: mProjectPP2/p2mass_area
      diff: diff_4
      hdr:
        source: ex_hdr
    out:
      [diff_out]


  mDiff5:
    run: mDiff.cwl
    in:
      p2mass1:
        source: mProjectPP4/p2mass
      p2mass2:
        source: mProjectPP3/p2mass
      p2mass1_area:
        source: mProjectPP4/p2mass_area
      p2mass2_area:
        source: mProjectPP3/p2mass_area
      diff: diff_5
      hdr:
        source: ex_hdr
    out:
      [diff_out]

  mFitplane1:
    run: mFitplane.cwl
    in:
      txt: fit_txt_1
      diff:
        source: mDiff1/diff_out
    out:
      [txt_out, diff_out]

  mFitplane2:
    run: mFitplane.cwl
    in:
      txt: fit_txt_2
      diff:
        source: mDiff2/diff_out
    out:
      [txt_out, diff_out]

  mFitplane3:
    run: mFitplane.cwl
    in:
      txt: fit_txt_3
      diff:
        source: mDiff3/diff_out
    out:
      [txt_out, diff_out]

  mFitplane4:
    run: mFitplane.cwl
    in:
      txt: fit_txt_4
      diff:
        source: mDiff4/diff_out
    out:
      [txt_out, diff_out]

  mFitplane5:
    run: mFitplane.cwl
    in:
      txt: fit_txt_5
      diff:
        source: mDiff5/diff_out
    out:
      [txt_out, diff_out]

  mConcatFit:
    run: mConcatFit.cwl
    in:
      statfile:
        source: ex_statfile
      fits_tbl: ex_fits_tbl
      txt1:
        source: mFitplane1/txt_out
      txt2:
        source: mFitplane2/txt_out
      txt3:
        source: mFitplane3/txt_out
      txt4:
        source: mFitplane4/txt_out
      txt5:
        source: mFitplane5/txt_out
    out:
      [tbl_out]

  mBgModel:
    run: mBgModel.cwl
    in:
      factor: ex_BM_factor
      pimages:
        source: ex_pimages
      fits_tbl:
        source: mConcatFit/tbl_out
      corr_tbl: ex_corr_tbl
    out:
      [corr_out]

  mBackground1:
    run: mBackground.cwl
    in:
      p2mass:
        source: mProjectPP1/p2mass
      p2mass_area:
        source: mProjectPP1/p2mass_area
      2mass:      2mass_1
      2mass_area: 2mass_area_1
      pimages:
        source: ex_pimages
      corr_tbl:
        source: mBgModel/corr_out
    out:
      [c2mass, c2mass_area]

  mBackground2:
    run: mBackground.cwl
    in:
      p2mass:
        source: mProjectPP2/p2mass
      p2mass_area:
        source: mProjectPP2/p2mass_area
      2mass:      2mass_2
      2mass_area: 2mass_area_2
      pimages:
        source: ex_pimages
      corr_tbl:
        source: mBgModel/corr_out
    out:
      [c2mass, c2mass_area]

  mBackground3:
    run: mBackground.cwl
    in:
      p2mass:
        source: mProjectPP3/p2mass
      p2mass_area:
        source: mProjectPP3/p2mass_area
      2mass:      2mass_3
      2mass_area: 2mass_area_3
      pimages:
        source: ex_pimages
      corr_tbl:
        source: mBgModel/corr_out
    out:
      [c2mass, c2mass_area]

  mBackground4:
    run: mBackground.cwl
    in:
      p2mass:
        source: mProjectPP4/p2mass
      p2mass_area:
        source: mProjectPP4/p2mass_area
      2mass:      2mass_4
      2mass_area: 2mass_area_4
      pimages:
        source: ex_pimages
      corr_tbl:
        source: mBgModel/corr_out
    out:
      [c2mass, c2mass_area]

  mImgtbl:
    run: mImgtbl.cwl
    in:
      cimages:
        source: ex_cimages
      c2mass1:
        source: mBackground1/c2mass
      c2mass2:
        source: mBackground2/c2mass
      c2mass3:
        source: mBackground3/c2mass
      c2mass4:
        source: mBackground4/c2mass
    out:
      [cimages_out]

  mAdd:
    run: mAdd.cwl
    in:
      cimages:
        source: mImgtbl/cimages_out
      hdr:
        source: ex_hdr
      mosaic: ex_mosaic
      c2mass1:
        source: mBackground1/c2mass
      c2mass2:
        source: mBackground2/c2mass
      c2mass3:
        source: mBackground3/c2mass
      c2mass4:
        source: mBackground4/c2mass
      c2mass_area1:
        source: mBackground1/c2mass_area
      c2mass_area2:
        source: mBackground2/c2mass_area
      c2mass_area3:
        source: mBackground3/c2mass_area
      c2mass_area4:
        source: mBackground4/c2mass_area
    out:
      [mosaic_out]

  mShrink:
    run: mShrink.cwl
    in:
      mosaic:
        source: mAdd/mosaic_out
      shrunken: ex_shrunken
    out:
      [shrunken_out]

  mJPEG:
    run: mJPEG.cwl
    in:
      shrunken:
        source: mShrink/shrunken_out
      jpeg: ex_jpeg
    out:
      [jpeg_out]
