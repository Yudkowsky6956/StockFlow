from src.utils.lazy_import import lazy_import

import_prompts = lazy_import("src.scripts.import_prompts", "import_prompts")
mark_files_as_done = lazy_import("src.scripts.mark_files_as_done", "mark_files_as_done")
clear_metadata = lazy_import("src.scripts.clear_metadata", "clear_metadata")
parse_sales_data = lazy_import("src.scripts.parse_sales_data", "parse_sales_data")
show_sales_infographics = lazy_import("src.scripts.show_sales_infographics", "show_sales_infographics")
organize_files = lazy_import("src.scripts.organize_files", "organize_files")

ALL_SCRIPTS_LIST = [
    import_prompts,
    mark_files_as_done,
    clear_metadata,
    parse_sales_data,
    show_sales_infographics,
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
    show_sales_infographics,
]