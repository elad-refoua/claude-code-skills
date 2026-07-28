# =========================================================================
# Build a manual-review CSV for diary numbering issues.
# Output format mirrors the researcher's familiar review file (e.g.,
# the AyE numbering review file in AIC studies) with optional helper
# columns appended at the end.
#
# Usage:
#   source("~/.claude/skills/diary-numbering-check/build_review_csv.R")
#   build_review_csv(
#     data       = my_data_post_corrections,
#     out_path   = "manual review/round2_to_fill.csv",
#     # optional: include the team's original review file so its _R values
#     #          are pre-filled in the output (so the researcher doesn't
#     #          lose prior edits)
#     prior_review_csv = "manual review/round1_to_fill.csv",
#     # which extra columns to add at the end of the output:
#     include_flags = c("is_in_duplicate", "has_calendar_skip",
#                       "suggested_NumberOfDay", "calendar_day_from_start"),
#     # which participants to include - defaults to ANY participant with at
#     # least one duplicate or calendar-skip issue
#     ids = NULL
#   )
# =========================================================================
suppressPackageStartupMessages({
  library(dplyr); library(tidyr); library(readr); library(lubridate)
})

build_review_csv <- function(data,
                              out_path,
                              prior_review_csv = NULL,
                              include_flags = c("is_in_duplicate",
                                                "has_calendar_skip",
                                                "suggested_NumberOfDay",
                                                "calendar_day_from_start"),
                              ids = NULL) {

  required <- c("id", "NumberOfDay", "NumberInDay", "StartDate", "ResponseId")
  missing  <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop("Required columns missing from data: ", paste(missing, collapse = ", "))
  }

  d <- data %>%
    mutate(
      id          = as.numeric(id),
      NumberOfDay = suppressWarnings(as.numeric(NumberOfDay)),
      NumberInDay = suppressWarnings(as.numeric(NumberInDay)),
      StartDate   = if (inherits(StartDate, "POSIXct") || inherits(StartDate, "Date")) {
                      as.POSIXct(StartDate)
                    } else {
                      suppressWarnings(parse_date_time(
                        as.character(StartDate),
                        orders = c("ymd HMS", "ymd HM", "mdy HM", "dmy HM",
                                   "ymd", "mdy", "dmy"),
                        quiet = TRUE))
                    },
      ResponseId  = as.character(ResponseId)
    )

  # Compute per-participant flags
  d <- d %>%
    group_by(id) %>%
    mutate(
      first_date            = min(StartDate),
      calendar_day_from_start = as.integer(as.Date(StartDate) - as.Date(first_date)) + 1L
    ) %>%
    ungroup() %>%
    mutate(
      suggested_NumberOfDay = calendar_day_from_start,
      has_calendar_skip     = if_else(NumberOfDay < calendar_day_from_start, "TRUE", "")
    ) %>%
    group_by(id, NumberOfDay, NumberInDay) %>%
    mutate(
      is_in_duplicate = if_else(
        n() > 1 & !is.na(id) & !is.na(NumberOfDay) & !is.na(NumberInDay),
        "TRUE", "")
    ) %>%
    ungroup()

  # Filter to problematic participants if `ids` not specified
  if (is.null(ids)) {
    problematic_ids <- d %>%
      filter(is_in_duplicate == "TRUE" | has_calendar_skip == "TRUE") %>%
      pull(id) %>% unique()
    ids <- problematic_ids
  }
  d_filtered <- d %>% filter(id %in% ids) %>% arrange(id, StartDate)

  # Load prior review _R values (if any) - so we preserve previous edits
  prior_R <- NULL
  if (!is.null(prior_review_csv) && file.exists(prior_review_csv)) {
    p <- read_csv(prior_review_csv, locale = locale(encoding = "UTF-8"),
                  show_col_types = FALSE, na = c("", "NA"))
    names(p) <- gsub("^\ufeff", "", names(p)); names(p) <- trimws(names(p))
    prior_R <- p %>% select(any_of(c("ResponseId", "SendTime_R",
                                      "NumberOfDay_R", "NumberInDay_R",
                                      "Notes", "id_R")))
  }

  # Build output in AyE format
  out <- d_filtered %>%
    mutate(StartDate_str = format(StartDate, "%m/%d/%Y %H:%M")) %>%
    transmute(
      StartDate          = StartDate_str,
      EndDate            = if ("EndDate" %in% names(d_filtered))
                              format(EndDate, "%m/%d/%Y %H:%M") else NA_character_,
      `Duration (in seconds)` = if ("Duration_in_seconds_" %in% names(d_filtered))
                                   Duration_in_seconds_ else NA_real_,
      Finished           = if ("Finished" %in% names(d_filtered)) Finished else NA_real_,
      RecordedDate       = if ("RecordedDate" %in% names(d_filtered))
                              format(RecordedDate, "%m/%d/%Y %H:%M") else NA_character_,
      ResponseId,
      RecipientFirstName = if ("RecipientFirstName" %in% names(d_filtered))
                              RecipientFirstName else NA_character_,
      id,
      SendTime           = if ("SendTime" %in% names(d_filtered))
                              as.character(SendTime) else NA_character_,
      NumberOfDay,
      NumberInDay,
      SendTime_R         = NA_character_,
      NumberOfDay_R      = NA_character_,
      NumberInDay_R      = NA_character_,
      Notes              = NA_character_,
      id_R               = NA_character_
    )

  # Merge prior _R values
  if (!is.null(prior_R)) {
    out <- out %>%
      select(-SendTime_R, -NumberOfDay_R, -NumberInDay_R, -Notes, -id_R) %>%
      left_join(prior_R, by = "ResponseId")
  }

  # Add helper columns
  helper_data <- d_filtered %>% select(ResponseId,
                                       is_in_duplicate,
                                       has_calendar_skip,
                                       suggested_NumberOfDay,
                                       calendar_day_from_start)
  out <- out %>% left_join(helper_data, by = "ResponseId")

  # Restrict helper columns to user's selection
  helper_cols_present <- intersect(include_flags, names(out))
  drop_helpers <- setdiff(c("is_in_duplicate", "has_calendar_skip",
                            "suggested_NumberOfDay", "calendar_day_from_start"),
                          helper_cols_present)
  if (length(drop_helpers) > 0) {
    out <- out %>% select(-any_of(drop_helpers))
  }

  # Ensure output dir exists
  dir.create(dirname(out_path), showWarnings = FALSE, recursive = TRUE)
  write_excel_csv(out, out_path)

  message("Review CSV written: ", out_path,
          " (", nrow(out), " rows, ", n_distinct(out$id), " participants)")
  invisible(out)
}
