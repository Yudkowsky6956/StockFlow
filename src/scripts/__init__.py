from src.utils.lazy_import import lazy_import

import_prompts = lazy_import("src.scripts.import_prompts", "ImportPrompts")
clear_metadata = lazy_import("src.scripts.clear_metadata", "ClearMetadata")
mark_files_as_done = lazy_import("src.scripts.mark_files_as_done", "MarkFilesAsDone")
parse_sales_data = lazy_import("src.scripts.parse_sales_data", "ParseSalesData")
show_sales_data = lazy_import("src.scripts.show_sales_data", "ShowSalesData")
organize_files = lazy_import("src.scripts.organize_files", "OrganizeFiles")

SCRIPTS_LIST = [
    import_prompts,
    mark_files_as_done,
    clear_metadata,
    parse_sales_data,
    show_sales_data,
]

DB_SCRIPTS_LIST = [
    import_prompts,
    mark_files_as_done,
]

FILES_SCRIPTS_LIST = [
    clear_metadata,
    organize_files,
]

INFOGRAPHICS_SCRIPTS_LIST = [
    parse_sales_data,
    show_sales_data,
]