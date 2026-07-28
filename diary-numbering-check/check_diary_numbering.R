# =========================================================================
# Diary numbering checker
# Usage: source this file, then call check_diary_numbering(data, ...)
# =========================================================================
suppressPackageStartupMessages({
  library(dplyr); library(tidyr); library(readr); library(lubridate)
})

#' Validate diary / ESM numbering for any dataset
#'
#' @param data data.frame with columns: id, NumberOfDay, NumberInDay,
#'   StartDate, ResponseId
#' @param expected_max_NumberInDay integer. Max prompts per day (default 4).
#' @param expected_max_NumberOfDay integer. Planned diary length in days
#'   (default 14). Values above this are flagged INFO only - not a failure,
#'   since restarts can legitimately push NumberOfDay higher.
#' @param calendar_tolerance_days integer. Allowed deviation between
#'   NumberOfDay and calendar-days-from-first-entry before flagging (default 1).
#' @param gap_threshold_days integer. Calendar gap (days) between consecutive
#'   diary entries that triggers a restart suspicion (default 7).
#' @param output_file character path. Where to save the markdown report.
#'   If NULL, no file is written.
#' @return list with: passed (logical), summary (data.frame), details (list),
#'   report_md (character)
check_diary_numbering <- function(data,
                                  expected_max_NumberInDay = 4L,
                                  expected_max_NumberOfDay = 14L,
                                  calendar_tolerance_days   = 1L,
                                  gap_threshold_days        = 7L,
                                  output_file = NULL) {

  required <- c("id", "NumberOfDay", "NumberInDay", "StartDate", "ResponseId")
  missing  <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop("Required columns missing from data: ", paste(missing, collapse = ", "))
  }

  # Normalize types
  d <- data %>%
    mutate(
      id           = as.numeric(id),
      NumberOfDay  = suppressWarnings(as.numeric(NumberOfDay)),
      NumberInDay  = suppressWarnings(as.numeric(NumberInDay)),
      StartDate    = if (inherits(StartDate, "POSIXct") || inherits(StartDate, "Date")) {
                       as.POSIXct(StartDate)
                     } else {
                       suppressWarnings(parse_date_time(
                         as.character(StartDate),
                         orders = c("ymd HMS", "ymd HM", "mdy HM", "dmy HM",
                                    "ymd", "mdy", "dmy"),
                         quiet = TRUE))
                     },
      ResponseId   = as.character(ResponseId)
    )

  # ----- 1) Duplicate (id, NumberOfDay, NumberInDay) triples -----
  dup_triples <- d %>%
    filter(!is.na(id), !is.na(NumberOfDay), !is.na(NumberInDay)) %>%
    group_by(id, NumberOfDay, NumberInDay) %>%
    filter(n() > 1) %>%
    ungroup() %>%
    arrange(id, NumberOfDay, NumberInDay, StartDate) %>%
    group_by(id, NumberOfDay, NumberInDay) %>%
    mutate(
      cycle_position = row_number(),
      gap_days_in_triple = round(as.numeric(
        difftime(max(StartDate), min(StartDate), units = "days")), 2),
      suggested_action = case_when(
        gap_days_in_triple < 1   ~ "drop_double_submission",
        gap_days_in_triple < 2   ~ "fix_wraparound",
        gap_days_in_triple >= gap_threshold_days ~ "keep_restart",
        TRUE                     ~ "review_manually"
      )
    ) %>%
    ungroup() %>%
    select(id, NumberOfDay, NumberInDay, ResponseId, StartDate,
           cycle_position, gap_days_in_triple, suggested_action)

  # ----- 2) ResponseId uniqueness -----
  dup_responseid <- d %>%
    group_by(ResponseId) %>%
    filter(n() > 1) %>%
    ungroup()

  # ----- 3) Calendar consistency -----
  # For each participant compute (calendar-days-since-first-entry + 1) and
  # compare with NumberOfDay.
  cal_check <- d %>%
    filter(!is.na(id), !is.na(StartDate), !is.na(NumberOfDay)) %>%
    group_by(id) %>%
    mutate(
      first_date         = min(StartDate),
      calendar_day_index = as.integer(as.Date(StartDate) - as.Date(first_date)) + 1L,
      day_delta          = NumberOfDay - calendar_day_index
    ) %>%
    ungroup() %>%
    filter(abs(day_delta) >= calendar_tolerance_days)
  cal_inconsistent <- cal_check %>%
    select(id, ResponseId, StartDate, NumberOfDay,
           expected_NumberOfDay = calendar_day_index, day_delta) %>%
    arrange(id, StartDate)

  # ----- 4) Wraparound suspected (consecutive entries where ND drops sharply) -----
  wrap_check <- d %>%
    filter(!is.na(id), !is.na(NumberOfDay), !is.na(StartDate)) %>%
    arrange(id, StartDate) %>%
    group_by(id) %>%
    mutate(
      prev_ND          = lag(NumberOfDay),
      prev_date        = lag(StartDate),
      ND_drop          = prev_ND - NumberOfDay
    ) %>%
    ungroup() %>%
    filter(!is.na(ND_drop) & ND_drop >= 3)
  wrap_suspect <- wrap_check %>%
    select(id, ResponseId, prev_NumberOfDay = prev_ND, NumberOfDay,
           StartDate, prev_StartDate = prev_date, drop = ND_drop)

  # ----- 5) NumberInDay out of range -----
  ni_out <- d %>%
    filter(!is.na(NumberInDay)) %>%
    filter(NumberInDay < 1 | NumberInDay > expected_max_NumberInDay) %>%
    select(id, ResponseId, StartDate, NumberInDay)

  # ----- 6) NumberOfDay <= 0 -----
  nd_invalid <- d %>%
    filter(!is.na(NumberOfDay), NumberOfDay <= 0) %>%
    select(id, ResponseId, StartDate, NumberOfDay)

  # ----- 7) Large gap (info only) -----
  gap_info <- d %>%
    filter(!is.na(id), !is.na(StartDate)) %>%
    arrange(id, StartDate) %>%
    group_by(id) %>%
    mutate(
      prev_date = lag(StartDate),
      gap_days  = as.numeric(difftime(StartDate, prev_date, units = "days"))
    ) %>%
    ungroup() %>%
    filter(!is.na(gap_days), gap_days > gap_threshold_days) %>%
    select(id, ResponseId, prev_StartDate = prev_date, StartDate, gap_days)

  # ----- 8) NumberOfDay > expected max (info only) -----
  nd_high_info <- d %>%
    filter(!is.na(NumberOfDay), NumberOfDay > expected_max_NumberOfDay) %>%
    select(id, ResponseId, StartDate, NumberOfDay)

  # ===== Summary =====
  summary_df <- tibble(
    check = c("duplicate_triples",
              "responseid_uniqueness",
              "calendar_consistency",
              "wraparound_suspected",
              "numberinday_out_of_range",
              "numberofday_negative_or_zero",
              "gap_too_large",
              "numberofday_above_expected_max"),
    severity = c("FAIL", "FAIL", "WARN", "WARN", "WARN", "FAIL", "INFO", "INFO"),
    count = c(nrow(dup_triples),
              nrow(dup_responseid),
              nrow(cal_inconsistent),
              nrow(wrap_suspect),
              nrow(ni_out),
              nrow(nd_invalid),
              nrow(gap_info),
              nrow(nd_high_info))
  ) %>%
    mutate(status = case_when(
      count == 0 ~ "PASS",
      severity == "INFO" ~ "INFO",
      severity == "WARN" ~ "WARN",
      TRUE       ~ "FAIL"
    ))

  passed <- !any(summary_df$status == "FAIL")

  # ===== Markdown report =====
  md <- c(
    "# Diary numbering check",
    "",
    paste0("**Generated:** ", format(Sys.time(), "%Y-%m-%d %H:%M:%S")),
    paste0("**Total rows:** ", nrow(d),
           "  *  **Total participants:** ", n_distinct(d$id)),
    paste0("**Overall:** ", if (passed) "PASS" else "FAIL"),
    "",
    "## Summary",
    "",
    paste(capture.output(print(summary_df, n = Inf)), collapse = "\n"),
    "",
    "## Detailed problems",
    ""
  )

  add_section <- function(title, df, msg_when_zero = "(none)") {
    md_new <- c(paste0("### ", title, " (", nrow(df), " rows)"), "")
    if (nrow(df) == 0) {
      md_new <- c(md_new, msg_when_zero, "")
    } else {
      md_new <- c(md_new, paste(capture.output(print(df, n = 200)), collapse = "\n"), "")
    }
    md_new
  }

  md <- c(md, add_section("duplicate_triples", dup_triples))
  md <- c(md, add_section("responseid_uniqueness (duplicates)", dup_responseid))
  md <- c(md, add_section("calendar_consistency (NumberOfDay disagrees with calendar)", cal_inconsistent))
  md <- c(md, add_section("wraparound_suspected (NumberOfDay drops >= 3)", wrap_suspect))
  md <- c(md, add_section("numberinday_out_of_range", ni_out))
  md <- c(md, add_section("numberofday_negative_or_zero", nd_invalid))
  md <- c(md, add_section("gap_too_large (between consecutive entries, info)", gap_info))
  md <- c(md, add_section(paste0("numberofday_above_expected_max (>", expected_max_NumberOfDay, ", info)"), nd_high_info))

  report_md <- paste(md, collapse = "\n")

  if (!is.null(output_file)) {
    writeLines(report_md, output_file, useBytes = TRUE)
  }

  invisible(list(
    passed     = passed,
    summary    = summary_df,
    details    = list(
      duplicate_triples         = dup_triples,
      responseid_duplicates     = dup_responseid,
      calendar_inconsistent     = cal_inconsistent,
      wraparound_suspect        = wrap_suspect,
      numberinday_out_of_range  = ni_out,
      numberofday_invalid       = nd_invalid,
      gap_too_large             = gap_info,
      numberofday_above_max     = nd_high_info
    ),
    report_md  = report_md
  ))
}
