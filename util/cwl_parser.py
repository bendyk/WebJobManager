try:
  from cwltool.load_tool import load_tool, fetch_document, validate_document
  from cwltool.resolver import tool_resolver
except:
  print("install cwltool for commonworkflowlanguage support")
  exit(-1)

class Parser:

  @staticmethod
  def parse_cwl(cwl_file):

    process_obj = None
    document_loader, workflowobj, uri = fetch_document(cwl_file, resolver=tool_resolver, fetcher_constructor=None)

    try:
      document_loader, avsc_names, process_obj, metada, uri \
        = validate_document(document_loader, 
                            workflowobj, 
                            uri, 
                            enable_dev=False, 
                            strict=True, 
                            preprocess_only=False,
                            fetcher_constructor=None)

    except ValueError:
      print("Syntax Error in CWL File: %s" % cwl_file)
      process_obj = None

    return process_obj       

  @staticmethod
  def parse_data(cwl_file):
    document_loader, workflowobj, uri = fetch_document(cwl_file, resolver=tool_resolver, fetcher_constructor=None)
    return workflowobj


