# =========================================================================
# Flag participants with any inter-diary gap > N days.
# Adds per-row columns has_long_gap (logical) and max_gap_days (numeric).
#
# Usage:
#   source("~/.claude/skills/diary-numbering-check/flag_long_gaps.R")
#   dat_with_flags <- flag_long_gaps(dat, gap_threshold_days = 7)
# =========================================================================
suppressPackageStartupMessages({
  library(dplyr); library(lubridate)
})

flag_long_gaps <- function(data, gap_threshold_days = 7) {

  required <- c("id", "StartDate")
  missing  <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop("Required columns missing: ", paste(missing, collapse = ", "))
  }

  d <- data %>%
    mutate(StartDate = if (inherits(StartDate, "POSIXct") || inherits(StartDate, "Date")) {
                          as.POSIXct(StartDate)
                        } else {
                          suppressWarnings(parse_date_time(
                            as.character(StartDate),
                            orders = c("ymd HMS", "ymd HM", "mdy HM", "dmy HM",
                                       "ymd", "mdy", "dmy"),
                            quiet = TRUE))
                        })

  gap_info <- d %>%
    filter(!is.na(id), !is.na(StartDate)) %>%
    arrange(id, StartDate) %>%
    group_by(id) %>%
    mutate(prev_date = lag(StartDate),
           gap_days  = as.numeric(difftime(StartDate, prev_date, units = "days"))) %>%
    summarise(
      max_gap_days = max(gap_days, na.rm = TRUE),
      .groups      = "drop"
    ) %>%
    mutate(max_gap_days = if_else(is.infinite(max_gap_days), NA_real_, max_gap_days),
           has_long_gap = !is.na(max_gap_days) & max_gap_days > gap_threshold_days)

  out <- data %>%
    select(-any_of(c("max_gap_days", "has_long_gap"))) %>%
    left_join(gap_info, by = "id")

  n_long <- sum(gap_info$has_long_gap)
  message("Participants with gap > ", gap_threshold_days, " days: ",
          n_long, " of ", nrow(gap_info))

  invisible(out)
}
