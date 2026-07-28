---
name: qualtrics-cleaning
description: "Qualtrics data import and cleaning workflow in R. Use when fetching surveys from Qualtrics API, merging male/female duplicate columns, combining multi-round surveys, cleaning problematic responses, and constructing scales."
---

# Qualtrics Data Import & Cleaning Skill

Comprehensive workflow for importing data directly from Qualtrics and cleaning it in R.

## IMPORTANT: Claude Workflow

When writing R code for Qualtrics data:
1. **Always prepare the COMPLETE R script** - not snippets
2. **Save the script to the project folder** before running
3. **Use `file.path()` for all paths** - never hardcode
4. **Create output folder if needed** at script start

---

## API Credentials

Store your Qualtrics API credentials securely (e.g., in a JSON file or environment variables). Never hardcode API keys in scripts.

### Credentials File Pattern
```json
{
  "accounts": {
    "ACCOUNT1": {
      "api_key": "<YOUR_API_KEY>",
      "base_url": "<YOUR_QUALTRICS_BASE_URL>"
    }
  }
}
```

---

## Required Packages
```r
library(qualtRics)
library(tibble)
library(tidyverse)
library(dplyr)
library(sjlabelled)
library(sjPlot)
```

## File Header
```r
rm(list=ls())
cat("\014")
#Sys.setlocale("LC_ALL", "Hebrew")
if (is.null(dev.list()) == FALSE){dev.off()}
```

---

## Qualtrics API Connection Function

```r
# Load credentials from a JSON file (never hardcode keys)
creds <- jsonlite::read_json("~/.credentials/qualtrics.json")

qualtricsConnect <- function(names, api_key, base_url) {
  qualtRics::qualtrics_api_credentials(
    api_key = api_key,
    base_url = base_url,
    install = FALSE
  )

  surveys <- qualtRics::all_surveys()
  surveys <- surveys %>% filter(grepl(names, name))

  # Remove empty surveys
  rows_to_remove <- c()
  for (i in 1:nrow(surveys)) {
    md <- qualtRics::metadata(surveyID = surveys$id[i])
    if (md$responsecounts$auditable == 0) {
      rows_to_remove <- c(rows_to_remove, i)
    }
  }

  if(length(rows_to_remove) > 0) {
    print("Removed surveys:")
    print(surveys[rows_to_remove,])
    surveys <- surveys[-rows_to_remove, ]
  }

  return(surveys)
}

# Usage:
# surveys <- qualtricsConnect("study 2.*BQ",
#                             api_key = creds$accounts$ACCOUNT1$api_key,
#                             base_url = creds$accounts$ACCOUNT1$base_url)
```

---

## File & Folder Management

### Path Setup Pattern
```r
# Define paths at the top of the script
project_path <- "<SET_YOUR_PATH>/PROJECT_NAME"
data_path <- file.path(project_path, "data")
output_path <- file.path(project_path, "output")
scripts_path <- file.path(project_path, "scripts")

# Create output folder if it doesn't exist
if (!dir.exists(output_path)) {
  dir.create(output_path, recursive = TRUE)
}
```

### File Naming Convention
```
{PROJECT}_{STUDY}_{QUESTIONNAIRE}_after_step_{N}.{ext}
```
Examples:
- `PROJ_study2_BQ_after_step_1.rds`
- `PROJ_study2_BQ_after_step_1.csv`
- `PROJ_study2_BQ_after_step_2.rds`

### Save RDS (Preferred - preserves attributes)
```r
saveRDS(data, file = file.path(output_path, "data_after_step_1.rds"))
```

### Save CSV (for sharing/review)
```r
write.csv(data,
          file = file.path(output_path, "data_after_step_1.csv"),
          fileEncoding = "UTF-8",
          row.names = FALSE)
```

### Load Data
```r
data <- readRDS(file = file.path(data_path, "data_after_step_1.rds"))
```

---

## Fetch Survey Data

```r
# Account 1 example
surveys <- qualtricsConnect("study 2.*BQ",
                            api_key = creds$accounts$ACCOUNT1$api_key,
                            base_url = creds$accounts$ACCOUNT1$base_url)

# Account 2 example
surveys <- qualtricsConnect("project.*wave 1",
                            api_key = creds$accounts$ACCOUNT2$api_key,
                            base_url = creds$accounts$ACCOUNT2$base_url)

# Download survey data
z <- qualtRics::fetch_survey(
  surveyID = surveys$id,
  verbose = TRUE,
  force_request = TRUE,
  label = FALSE,          # Get numeric values, not labels
  convert = FALSE,        # Don't auto-convert types
  include_display_order = TRUE
)

# Remove suffix from duplicated column names (male/female)
names(z) <- gsub("\\...[0-9]+$", "", names(z))
```

---

## Merge Duplicate Columns (Male/Female)

When surveys have separate columns for male and female participants with identical variable names:

```r
merge_duplicate_columns <- function(df) {
  dup_cols <- names(df)[duplicated(names(df))]

  dup_counts <- table(dup_cols)
  if(any(dup_counts > 1)){
    print(paste("Columns duplicated more than twice:",
                names(dup_counts)[which(dup_counts > 1)]))
  }

  unique_cols <- unique(dup_cols)

  for (col_name in unique_cols) {
    cols_with_same_name <- df[, which(names(df) == col_name), drop = FALSE]

    has_conflict <- !is.na(cols_with_same_name[[1]]) & !is.na(cols_with_same_name[[2]])
    if (any(has_conflict)) {
      warning(paste0(
        "Conflict for '", col_name, "' at rows: ",
        paste(df$ResponseId[has_conflict], collapse = ", ")
      ))
    }

    merged_col <- ifelse(is.na(cols_with_same_name[[1]]),
                         cols_with_same_name[[2]],
                         cols_with_same_name[[1]])
    attributes(merged_col) <- attributes(cols_with_same_name[[1]])
    df[[col_name]] <- merged_col
  }

  df <- df[, !duplicated(names(df))]
  return(df)
}

all <- merge_duplicate_columns(z)
```

---

## Merge Multiple Surveys (Rounds)

For multi-round studies with separate surveys per round:

```r
merge_datasets <- function(dataset_names) {
  merged_df <- data.frame()
  merge_summaries <- list()

  for (i in 1:length(dataset_names)) {
    all_datasets <- ls(envir = .GlobalEnv)
    matching_datasets <- grep(dataset_names[i], all_datasets, value = TRUE, fixed = TRUE)

    for (j in 1:length(matching_datasets)) {
      current_df <- get(matching_datasets[j], envir = .GlobalEnv)

      study <- gsub(".*study ([0-9]+).*", "\\1", matching_datasets[j], ignore.case = TRUE)
      wave <- gsub(".*wave ([0-9]+).*", "\\1", matching_datasets[j], ignore.case = TRUE)

      if (grepl("round", matching_datasets[j], ignore.case = TRUE)) {
        round <- gsub(".*round ([0-9]+).*", "\\1", matching_datasets[j], ignore.case = TRUE)
      } else if (grepl("pilot", matching_datasets[j], ignore.case = TRUE)) {
        round <- "0"
      } else {
        round <- NA
      }

      current_df$study <- as.numeric(study)
      current_df$round <- as.numeric(round)
      current_df$wave <- as.numeric(wave)

      if (nrow(merged_df) == 0) {
        merged_df <- current_df
      } else {
        merged_df <- merge(merged_df, current_df, all = TRUE)
        current_attributes <- lapply(current_df, attributes)
        for (var in names(current_attributes)) {
          if (var %in% names(merged_df)) {
            attributes(merged_df[[var]]) <- current_attributes[[var]]
          }
        }
      }
    }
  }

  return(list('merged_df' = merged_df, 'merge_summaries' = merge_summaries))
}
```

---

## Basic Cleaning

### Add Time Variables
```r
all$StartDate <- as.POSIXct(all$StartDate)
all$EndDate <- as.POSIXct(all$EndDate)
all$hours_diff <- as.numeric(difftime(all$EndDate, all$StartDate, units = "hours"))
```

### Create Numeric ID
```r
all2 <- all %>%
  dplyr::mutate(id = as.numeric(contact_id))

# Or with multiple ID sources
all2 <- all %>%
  dplyr::mutate(
    id = dplyr::case_when(
      round == 0 ~ as.numeric(contact_id),
      round %in% 1:4 ~ as.numeric(client_id),
      TRUE ~ NA_real_
    )
  )
```

### Filter by ID Range
```r
# Example: filter to valid participant ID ranges for your study
all3 <- all2 %>%
  filter((id >= 1001 & id <= 1999) | (id >= 2001 & id <= 2999))
```

### Visualize ID Distribution
```r
p <- sjPlot::plot_frq(all3$id)
print(p)
```

### Mark and Remove Problem Cases
```r
multi_responses <- c()   # Add IDs that answered twice or more
problematic <- c()       # Add IDs with timing issues, etc.
withdrew <- c()          # Add IDs that withdrew from study

all3 <- all3 %>%
  mutate(finish = as.numeric(Progress == 100))

all4 <- all3 %>%
  filter(!(finish == 0 & id %in% multi_responses))

all5 <- all4 %>%
  mutate(problem = if_else(id %in% problematic, 1, 0))
```

### Check for Duplications
```r
result_table <- all5 %>%
  group_by(id) %>%
  summarise(
    all_names = paste(unique(RecipientFirstName), collapse = ", "),
    all_emails = paste(unique(RecipientEmail), collapse = ", ")
  ) %>%
  ungroup()
```

---

## Scale Construction (Step 2)

### Pattern: Reverse Scoring
```r
# 4-point scale: recode 4 as 1, 3 as 2, etc.
data <- data %>%
  mutate(across(c("TAI_1"), ~ 5 - ., .names = "{.col}_reversed"))

# 7-point scale
data <- data %>%
  mutate(across(c("Big5_2", "Big5_4", "Big5_6"), ~ 8 - ., .names = "{.col}_reversed"))
```

### Pattern: Subscale with rowSums
```r
curr_data <- data[c("TAI_3","TAI_4","TAI_5","TAI_6","TAI_7")]
curr_data <- curr_data %>% mutate(TAI_Worry = rowSums(curr_data, na.rm = TRUE))
data$TAI_Worry <- curr_data$TAI_Worry
```

### Pattern: Subscale with rowMeans
```r
curr_data <- data[c("YSQ_1","YSQ_19","YSQ_37","YSQ_55","YSQ_73")]
curr_data <- curr_data %>% mutate(YSQ_emotionaldeprivation = rowMeans(curr_data, na.rm = TRUE))
data$YSQ_emotionaldeprivation <- curr_data$YSQ_emotionaldeprivation
```

### Pattern: Select Variables by Prefix
```r
curr_data <- data[, grep("YSQ", colnames(data), ignore.case = TRUE)]
# Or with tidyverse
curr_data <- data %>% select(starts_with("Big5_"))
```

### Pattern: Total Score Excluding Variables
```r
data <- data %>%
  mutate(TAI_TotalScore = select(., starts_with("TAI_")) %>%
           select(-c(TAI_1, TAI_Worry, TAI_Emotionality)) %>%
           rowSums(na.rm = TRUE))
```

### Pattern: Ipsatized Scores (IIP Circumplex)
```r
# Step 1: Create ipsatized items
data <- data %>%
  mutate(across(c(IIP_1:IIP_32), ~ . - IIP_TotalScore, .names = "{.col}_ips"))

# Step 2: Calculate ipsatized subscales
curr_data <- data[c("IIP_10_ips","IIP_21_ips","IIP_24_ips","IIP_28_ips")]
curr_data <- curr_data %>% mutate(IIP_PA_ips = rowMeans(curr_data, na.rm = TRUE))
data$IIP_PA_ips <- curr_data$IIP_PA_ips

# Step 3: Calculate circumplex axes
data <- data %>%
  mutate(
    IIP_DOM = IIP_PA_ips - IIP_HI_ips + 0.707 * (IIP_NO_ips + IIP_BC_ips - IIP_FG_ips - IIP_JK_ips),
    IIP_LOV = IIP_LM_ips - IIP_DE_ips + 0.707 * (IIP_NO_ips + IIP_BC_ips - IIP_FG_ips - IIP_JK_ips)
  )
```

### Pattern: Standardized Scores (Z-scores)
```r
DERS_mean <- mean(data$DERS_TotalScore, na.rm = TRUE)
DERS_sd <- sd(data$DERS_TotalScore, na.rm = TRUE)

data <- data %>%
  mutate(DERS_ZScore = (DERS_TotalScore - DERS_mean) / DERS_sd)
```

### Pattern: Binary Cut-off
```r
data <- data %>%
  mutate(
    ASRS_highly_consistent = ifelse(ASRS_count >= 4, 1, 0),
    SPIN_CutOff = ifelse(SPIN_TotalScore >= 19, 1, 0)
  )
```

---

## Code Style Notes

1. **Create temporary data frames** for each scale (`curr_data`, `curr_data2`)
2. **Copy results back** to main data frame explicitly
3. **Comment references** to scaling manuals/articles
4. **Keep original variables** when creating reversed versions
5. **Use explicit item lists** rather than regex for subscales
6. **Section headers** with `#SCALE_NAME----` format
7. **Always use `file.path()`** for paths
8. **Save both RDS and CSV** at each step for verification

---

## Key Qualtrics Variables

Standard Qualtrics metadata columns:
```
StartDate, EndDate, Status, IPAddress, Progress, Duration (in seconds),
Finished, RecordedDate, ResponseId, RecipientLastName, RecipientFirstName,
RecipientEmail, ExternalReference, LocationLatitude, LocationLongitude,
DistributionChannel, UserLanguage
```

Custom ID columns (project-specific):
```
surveyID, contact_id, client_id, SendTime, NumberOfDay, NumberInDay,
distribution, distributionId
```

---

## Complete Script Template

```r
## Cleans R studio ----
rm(list=ls())
cat("\014")
#Sys.setlocale("LC_ALL", "Hebrew")
if (is.null(dev.list()) == FALSE){dev.off()}

## Load packages ----
library(qualtRics)
library(tibble)
library(tidyverse)
library(dplyr)
library(sjlabelled)
library(sjPlot)

## Define paths ----
project_path <- "<SET_YOUR_PATH>/PROJECT_NAME"
output_path <- file.path(project_path, "output")

if (!dir.exists(output_path)) {
  dir.create(output_path, recursive = TRUE)
}

## Load credentials and define API function ----
# See qualtricsConnect() function defined above

## Fetch data ----
surveys <- qualtricsConnect("study 2.*BQ",
                            api_key = "<YOUR_API_KEY>",
                            base_url = "<YOUR_QUALTRICS_BASE_URL>")
z <- qualtRics::fetch_survey(surveyID = surveys$id,
                             verbose = TRUE, force_request = TRUE,
                             label = FALSE, convert = FALSE,
                             include_display_order = TRUE)
names(z) <- gsub("\\...[0-9]+$", "", names(z))

## Merge duplicates ----
all <- merge_duplicate_columns(z)

## Clean data ----
# ... cleaning steps ...

## Save output ----
saveRDS(all, file = file.path(output_path, "data_after_step_1.rds"))
write.csv(all, file = file.path(output_path, "data_after_step_1.csv"),
          fileEncoding = "UTF-8", row.names = FALSE)
```
