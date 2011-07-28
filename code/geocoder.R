#
# July 28, 2011
#

library(XML) # Google
library(geonames) # geonames.org

geocoder.get_first_text <- function (xml, tag_names) {
  for (tag_name in tag_names) {
    elements <- xmlElementsByTagName(xml, tag_name, recursive = TRUE)
    if (length(elements) > 0) {
      return(xmlValue(elements[[1]]))
    }
  }
  
  return(NA)
}

#
# Google
#

geocoder.Google.parse_place <- function (placemark_xml) {
  location <- geocoder.get_first_text(placemark_xml, c("address", "name"))
  coords <- geocoder.get_first_text(placemark_xml, "coordinates")
  coords <- strsplit(coords, ",")[[1]]
  longitude <- as.numeric(coords[1])
  latitude <- as.numeric(coords[2])
  
  return(list(
    location = location,
    longitude = longitude,
    latitude = latitude
  ))
}

geocoder.Google <- function (q, key = NULL, resource = "maps",
  first_only = FALSE) {
  g_url <- sprintf("http://maps.google.com/%s?q=%s&output=kml", resource, q)
  if (is.null(key) == FALSE) {
    g_url <- sprintf("%s&key=%s", g_url, key)
  }
  
  x <- xmlTreeParse(g_url, isURL = TRUE)
  places_list <- xmlElementsByTagName(x$doc$children$kml, "Placemark",
    recursive = TRUE)
  if (length(places_list) == 0) {
    return(NA)
  } else if (first_only == TRUE) {
    places_list <- places_list[1]
  }
  
  places <- list()
  for (place_xml in places_list) {
    place <- geocoder.Google.parse_place(place_xml)
    if (is.na(place$longitude) == FALSE) {
      places <- c(places, list(place))
    }
  }
  
  if (length(places) == 0) {
    return(NA)
  } else {
    return(places)
  }
}

#
# geonames
#

geocoder.geonames.parse_place <- function (row) {
  return(list(
    location = row$name,
    longitude = row$lng,
    latitude = row$lat
  ))
}

geocoder.geonames <- function (q, ..., first_only = FALSE) {
  places_df <- suppressWarnings(GNsearch(q = q, ...))
  
  i_max <- nrow(places_df)
  if (i_max == 0) {
    return(NA)
  } else if (first_only == TRUE) {
    return(list(geocoder.geonames.parse_place(places_df[1, ])))
  } else {
    places <- list()
    for (i in 1:i_max) {
      place <- geocoder.geonames.parse_place(places_df[i, ])
      places <- c(places, list(place))
    }
    
    return(places)
  }
}
