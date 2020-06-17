# devtools::install_github('charlie86/spotifyr')
library('spotifyr')
library(purrr)
library(lubridate)
library(knitr)
library(plyr)
library(ggplot2)
library(tidyr)
require(sqldf)
library(stringr)
library(dplyr)
library(googlesheets4)

id <- 'a498307d278a4569a85f21de1f78d5d7'
secret <- '331e4c3def7c4b7a97a0e10e1901cfa9'
Sys.setenv(SPOTIFY_CLIENT_ID = id)
Sys.setenv(SPOTIFY_CLIENT_SECRET = secret)
access_token <- get_spotify_access_token()

top_songs <- read.csv('yearly_hot_100_chart.csv', header = TRUE, sep = ';')

# Define function to clean hot 100 billboard csv
get_top_song_clean <- function(top_songs, x_songs_per_week) {
  
  top_songs_list <- top_songs%>%
    dplyr::filter(rank == c(1:x_songs_per_week))%>%
    select(c('name','artist'))
  
  top_songs_list$name <- tolower(top_songs_list$name)
  
  top_songs_list <- top_songs_list %>% 
    separate(artist, into = paste0('artist', 1:3), sep = ',')%>%
    separate(artist1, into = paste0('artist', 1:3), sep = ' Featuring')%>%
    separate(artist1, into = paste0('artist', 1:3), sep = ' &')%>%
    select(c(1,2))
  
  return(top_songs_list)
  
}

# Run function
top_songs_list <- get_top_song_clean(top_songs, 10)


# FOR LOOP
track_features <- NULL

for (i in 1:nrow(top_songs_list))     {
  search <- spotifyr::search_spotify(as.character(top_songs_list$name[i]), 'track')
  colnames(search) <- paste0('track_', colnames(search))
  search$track_name <- tolower(search$track_name)
  
  search <- search %>%
    tidyr::unnest(cols = 'track_artists') %>%
    dplyr::group_by(track_id) %>%
    dplyr::mutate(row_number = 1:n(),
                  artists = name) %>%
    dplyr::ungroup() %>%
    dplyr::filter(row_number == 1)
  
  filtered_search <- search%>%
    dplyr::filter(name == top_songs_list$artist1[i])%>%
    dplyr::filter(track_name == top_songs_list$name[i])

  if(nrow(filtered_search) == 0){
    filtered_search <- search%>%
      filter(rank(desc(track_popularity))<=1)
  }else{
    filtered_search <- filtered_search%>%
      filter(rank(desc(track_popularity))<=1)
  }
  
  
  audio <- spotifyr::get_track_audio_features(filtered_search$track_id)
  
  audio$track_name <- top_songs_list$name[i]
  audio$spotify_track_name <- filtered_search$track_name
  
  track_features <- dplyr::bind_rows(track_features, audio)
  
}

gs4_auth()
1
ss <- 'https://docs.google.com/spreadsheets/d/16wFvXQFtq_RhjiK1dPKUSMEcQ-9meP3hYMUPz5YQY8c/edit#gid=0'
to_gs <- track_features[,c(1:14,17:20)]
to_gs %>% 
  sheet_write(ss, sheet = "track_features")

