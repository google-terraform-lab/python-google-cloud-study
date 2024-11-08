variable dataset_id {
    type = string
}

variable name {
    type = string
}

variable compressed {
    type = bool
}

variable path {
    type = string
}

resource "google_bigquery_table" "compressed" {
  dataset_id = var.dataset_id
  table_id   = var.name


  external_data_configuration {
    autodetect    = true
    source_format = "NEWLINE_DELIMITED_JSON"
    compression = var.compressed == true ? "GZIP" : "NONE"
    
    dynamic "hive_partitioning_options" {
      for_each = var.compressed == true ? [1] : []
      content {
        mode              = "AUTO"
        source_uri_prefix = var.path
      }
    }

    source_uris = [
      "${var.path}*",
    ]
  }

  deletion_protection=false
}