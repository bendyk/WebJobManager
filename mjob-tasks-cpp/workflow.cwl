cwlVersion: v1.0
class: Workflow
inputs:
  wf_input  : string
  mjob2_out : string
  mjob3_out : string

outputs:
  fileout:
    type: File
    outputSource: mjob4_step/fileout

steps:
  mjob1_step:
    run: mjob1.cwl
    in:
      text: wf_input
    out: [fileout1, fileout2]

  mjob2_step:
    run: mjob2.cwl
    in:
      file1:
        source: mjob1_step/fileout1
      fout: mjob2_out
    out: [fileout]

  mjob3_step:
    run: mjob2.cwl
    in:
      file1:
        source: mjob1_step/fileout2
      fout: mjob3_out
    out: [fileout]

  mjob4_step:
    run: mjob4.cwl
    in:
      file1:
        source: mjob2_step/fileout
      file2:
        source: mjob3_step/fileout
    out: [fileout]
