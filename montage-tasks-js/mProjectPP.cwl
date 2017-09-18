cwlVersion: v1.0
class: CommandLineTool
baseCommand: mProjectPP.js

inputs:
  factor:
    type: string
    inputBinding:
      prefix: -x
      position: 1
  2mass:
    type: File
    inputBinding:
      prefix: -X
      position: 2
  2mass_out:
    type: string
    inputBinding:
      position: 3
      valueFrom: p$(inputs.2mass)
  hdr:
    type: File
    inputBinding:
      position: 4
  2mass_area_out:
    type: string

outputs:
  p2mass:
    type: File
    outputBinding:
      glob: $(inputs.2mass_out)
  p2mass_area:
    type: File
    outputBinding:
      glob: p$(inputs.2mass_area_out)
