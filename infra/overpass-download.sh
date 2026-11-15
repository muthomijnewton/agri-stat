# Sourced by the Overpass image before its normal initialization.
# Keep a dated source and partial file across connection resets/container restarts.
agristat_download() {
    local db_root="${OVERPASS_DB_DIR:-/db}"
    [[ -f "$db_root/init_done" ]] && return 0
    local cache="$db_root/download-cache"
    mkdir -p "$cache"
    if [[ ! -s "$cache/source.url" ]]; then
        curl --fail --silent --show-error --location --head --connect-timeout 20 --max-time 90 \
            --output /dev/null --write-out '%{url_effective}' "$OVERPASS_PLANET_URL" > "$cache/source.url.tmp"
        test -s "$cache/source.url.tmp"
        mv "$cache/source.url.tmp" "$cache/source.url"
    fi
    local source expected actual
    source=$(cat "$cache/source.url")
    curl --fail --silent --show-error --location --connect-timeout 20 --max-time 90 \
        --retry 5 --retry-delay 5 "${source}.md5" -o "$cache/source.md5.tmp"
    expected=$(awk 'NR==1 {print $1}' "$cache/source.md5.tmp")
    [[ "$expected" =~ ^[[:xdigit:]]{32}$ ]] || { echo 'Invalid source checksum'; return 1; }
    # Retain an existing initial download if one was started by the original image.
    # Its identity is unknown, so the final full checksum must match before import.
    if [[ ! -e "$cache/kenya.osm.pbf" && -s "$db_root/planet.osm.bz2" ]]; then
        cp "$db_root/planet.osm.bz2" "$cache/kenya.osm.pbf"
    fi
    local attempt
    for attempt in $(seq 1 60); do
        if [[ -s "$cache/kenya.osm.pbf" ]]; then
            actual=$(md5sum "$cache/kenya.osm.pbf" | awk '{print $1}')
            [[ "$actual" == "$expected" ]] && break
        fi
        echo "Kenya download attempt $attempt: resuming at $(stat -c %s "$cache/kenya.osm.pbf" 2>/dev/null || echo 0) bytes"
        if curl --write-out '%{http_code}' --fail --location --continue-at - --connect-timeout 20 --speed-limit 1024 --speed-time 120 \
            --max-time 1800 --output "$cache/kenya.osm.pbf" "$source" > "$cache/http-status"; then
            actual=$(md5sum "$cache/kenya.osm.pbf" | awk '{print $1}')
            if [[ "$actual" == "$expected" ]]; then break; fi
            # A legacy partial may belong to yesterday's extract. Preserve it, then retry cleanly.
            echo 'Checksum mismatch: preserving incompatible download and restarting the pinned extract.'
            mv "$cache/kenya.osm.pbf" "$cache/incompatible-$(date +%s).pbf"
        else
            local curl_status=$?
            if [[ "$curl_status" == 33 || "$(cat "$cache/http-status")" == 416 ]]; then
                echo 'Source cannot resume this partial; preserving it before a clean retry.'
                mv "$cache/kenya.osm.pbf" "$cache/incompatible-$(date +%s).pbf"
            fi
        fi
        sleep "${OVERPASS_DOWNLOAD_RETRY_DELAY:-10}"
    done
    [[ -s "$cache/kenya.osm.pbf" ]] || return 1
    actual=$(md5sum "$cache/kenya.osm.pbf" | awk '{print $1}')
    [[ "$actual" == "$expected" ]] || { echo 'Download incomplete; partial retained for next restart.'; return 1; }
    echo 'Kenya extract checksum verified. Starting local database import.'
    export OVERPASS_PLANET_URL="file://$cache/kenya.osm.pbf"
}
agristat_download
