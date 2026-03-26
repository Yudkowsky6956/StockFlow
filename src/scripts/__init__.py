from src.utils.lazy_import import lazy_import

import_prompts = lazy_import("src.scripts.import_prompts", "ImportPrompts")
import_prompts_csv = lazy_import("src.scripts.import_prompts_csv", "ImportPromptsCSV")
clear_metadata = lazy_import("src.scripts.clear_metadata", "ClearMetadata")
mark_files_as_done = lazy_import("src.scripts.mark_files_as_done", "MarkFilesAsDone")
parse_sales_data = lazy_import("src.scripts.parse_sales_data", "ParseSalesData")
show_sales_data = lazy_import("src.scripts.show_sales_data", "ShowSalesData")
organize_files = lazy_import("src.scripts.organize_files", "OrganizeFiles")
print_last_message = lazy_import("src.scripts.print_last_message", "PrintLastMessage")

SCRIPTS_LIST = [
    import_prompts,
    import_prompts_csv,
    mark_files_as_done,
    clear_metadata,
    parse_sales_data,
    show_sales_data,
    print_last_message,
]

DB_SCRIPTS_LIST = [
    import_prompts,
    import_prompts_csv,
    mark_files_as_done,
]

FILES_SCRIPTS_LIST = [
    clear_metadata,
    organize_files,
    print_last_message,
]

INFOGRAPHICS_SCRIPTS_LIST = [
    parse_sales_data,
    show_sales_data,
]