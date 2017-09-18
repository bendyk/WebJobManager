cwlVersion: v1.0
class: CommandLineTool
baseCommand: mConcatFit.js

arguments: ["."]

inputs:
  statfile:
    type: File
    inputBinding:
      position: 1
  fits_tbl:
    type: string
    inputBinding:
      position: 2
  txt1:
    type: File
  txt2:
    type: File
  txt3:
    type: File
  txt4:
    type: File
  txt5:
    type: File
  
outputs:
  tbl_out:
    type: File
    outputBinding:
      glob: $(inputs.fits_tbl)
