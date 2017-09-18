cwlVersion: v1.0
class: CommandLineTool
baseCommand: mDiff.js

inputs:
  p2mass1:
    type: File
    inputBinding:
      position: 1
  p2mass2:
    type: File
    inputBinding:
      position: 2
  diff:
    type: string
    inputBinding:
      position: 3
  hdr:
    type: File
    inputBinding:
      position: 4
  p2mass1_area:
    type: File
  p2mass2_area:
    type: File
outputs:
  diff_out:
    type: File
    outputBinding:
      glob: $(inputs.diff)
