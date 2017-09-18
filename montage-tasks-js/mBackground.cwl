cwlVersion: v1.0
class: CommandLineTool
baseCommand: mBackground.js

inputs:
  p2mass:
    type: File
    inputBinding:
      prefix: -t
      position: 1
      
  c2mass_out:
    type: string
    inputBinding:
      position: 2
      valueFrom: c$(inputs.2mass)

  pimages:
    type: File
    inputBinding:
      position: 3

  corr_tbl:
    type: File
    inputBinding:
      position: 4

  2mass:
    type: string
  2mass_area:
    type: string
  p2mass_area:
    type: File
  
outputs:
  c2mass:
    type: File
    outputBinding:
      glob: $(inputs.c2mass_out)
  c2mass_area:
    type: File
    outputBinding:
      glob: c$(inputs.2mass_area)
