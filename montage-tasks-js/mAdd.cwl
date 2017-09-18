cwlVersion: v1.0
class: CommandLineTool
baseCommand: mAdd.js

inputs:
  cimages:
    type: File
    inputBinding:
      prefix: -e
      position: 1
  hdr:
    type: File
    inputBinding:
      position: 2
  mosaic:
    type: string
    inputBinding:
      position: 3
  c2mass1:
    type: File
  c2mass2:
    type: File
  c2mass3:
    type: File
  c2mass4:
    type: File
  c2mass_area1:
    type: File
  c2mass_area2:
    type: File
  c2mass_area3:
    type: File
  c2mass_area4:
    type: File

outputs:
  mosaic_out:
    type: File
    outputBinding:
      glob: $(inputs.mosaic)
