cwlVersion: v1.0
class: CommandLineTool
baseCommand: mBgModel.js

inputs:
  factor:
    type: string
    inputBinding:
      prefix: -i
      position: 1
  pimages:
    type: File
    inputBinding:
      position: 2
  fits_tbl:
    type: File
    inputBinding:
      position: 3
  corr_tbl:
    type: string
    inputBinding:
      position: 4
  
outputs:
  corr_out:
    type: File
    outputBinding:
      glob: $(inputs.corr_tbl)
